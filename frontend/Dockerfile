# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY ./frontend /app/frontend
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
