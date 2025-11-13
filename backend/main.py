import os
import re
import uuid
import sqlite3
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from openai import OpenAI

# Import your sql_utils
from backend.sql_utils import run_select, validate_select_sql, append_message, get_recent_messages

# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "../ecommerce.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in your .env file")

# -------------------------------------------------------------------
# FastAPI setup
# -------------------------------------------------------------------
app = FastAPI(title="E-Commerce NL → SQL API (OpenAI only)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Request model
# -------------------------------------------------------------------
class QueryIn(BaseModel):
    prompt: str
    conversation_id: str = None
    limit: int = 100

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def extract_sql_from_text(text: str) -> str:
    """Extract SQL code block from LLM output."""
    m = re.search(r"```sql\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"```([\s\S]*?)```", text)
    if m2:
        return m2.group(1).strip()
    text = re.sub(r"(?i)^sql\s*[:\-]\s*", "", text).strip()
    return text

def call_openai(messages: list, model: str):
    """Call OpenAI API using SDK >=1.0.0."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=512
    )
    # Return assistant content
    return resp.choices[0].message.content

# -------------------------------------------------------------------
# SQL generation
# -------------------------------------------------------------------
def generate_sql(prompt: str, conv_id: str = None, recent_messages_limit: int = 8) -> str:
    table_hint = """
customers(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state),
orders(order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at,
       order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, freight_value),
order_items(order_id, order_item_id, product_id, seller_id, shipping_limit_date, price),
payments(order_id, payment_sequential, payment_type, payment_installments, payment_value),
products(product_id, product_category_name, product_name_length, product_description_length,
         product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm),
sellers(seller_id, seller_zip_code_prefix, seller_city, seller_state),
order_reviews(review_id, order_id, review_score, review_comment_title, review_comment_message,
              review_creation_date, review_answer_timestamp),
geolocation(geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state),
product_category_name_translation(product_id, product_category_name, product_category_name_english)
"""

    system = (
        "You convert plain English questions about an e-commerce SQLite database "
        "into a single valid SQLite SELECT query only. Respond with only the SQL query."
    )

    messages = [{"role": "system", "content": system}]

    if conv_id:
        recent = get_recent_messages(DB_PATH, conv_id, limit=recent_messages_limit)
        for m in recent:
            role = "user" if m["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": m["content"]})

    user_content = f"{prompt}\n\n-- Table hints: {table_hint}"
    messages.append({"role": "user", "content": user_content})

    try:
        content = call_openai(messages, OPENAI_MODEL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API call failed: {str(e)}")

    return extract_sql_from_text(content)

# -------------------------------------------------------------------
# API endpoints
# -------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "provider": "openai"}

@app.post("/query")
async def query(q: QueryIn):
    if not q.prompt or not q.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt")

    conv_id = q.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"

    # Log user message
    append_message(DB_PATH, conv_id, "user", q.prompt)

    try:
        # Generate SQL
        generated = generate_sql(q.prompt, conv_id=conv_id)
        sql = generated.strip().rstrip(";")

        # Apply LIMIT if not present
        if re.search(r"(?i)\bLIMIT\b", sql) is None and isinstance(q.limit, int) and q.limit > 0:
            sql = f"{sql} LIMIT {q.limit}"

        # Validate & execute SQL
        safe_sql = validate_select_sql(sql)
        result = run_select(DB_PATH, safe_sql)

        # Log assistant messages
        append_message(DB_PATH, conv_id, "assistant", safe_sql)
        summary = f"Returned {len(result['rows'])} rows."
        append_message(DB_PATH, conv_id, "assistant", summary)

        return {
            "conversation_id": conv_id,
            "sql": safe_sql,
            "result": result,
            "rows_count": len(result["rows"])
        }

    except Exception as e:
        tb = traceback.format_exc()
        print("==== /query ERROR TRACEBACK ====")
        print(tb)
        print("==== END TRACEBACK ====")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
