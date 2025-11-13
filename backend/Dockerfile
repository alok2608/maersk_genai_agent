# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY ./backend /app/backend
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env

RUN pip install --no-cache-dir -r /app/requirements.txt

# expose port used by uvicorn
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
