import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "../ecommerce.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}

def load_csv_to_sqlite(conn, table_name, csv_file):
    """Load a single CSV file into a SQLite table."""
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ Loaded {table_name} ({len(df)} rows)")

def main():
    """Load all dataset CSVs into SQLite database."""
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    conn = sqlite3.connect(DB_PATH)
    try:
        for table, filename in TABLE_FILES.items():
            csv_path = os.path.join(DATA_DIR, filename)
            if os.path.exists(csv_path):
                load_csv_to_sqlite(conn, table, csv_path)
            else:
                print(f"⚠️ Skipping {table}: {filename} not found.")
        print("\n🎉 All data loaded successfully into", DB_PATH)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
