FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask psycopg2-binary prometheus_client


COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
