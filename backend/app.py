from flask import Flask, jsonify, Response
import os
import psycopg2
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# -----------------------------
# PROMETHEUS METRICS DEFINITIONS
# -----------------------------
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests received')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds')

# -----------------------------
# ROUTES
# -----------------------------
@app.before_request
def before_request():
    REQUEST_COUNT.inc()

@app.route('/')
def home():
    start_time = time.time()
    message = {"message": "Flask backend is running!"}
    REQUEST_LATENCY.observe(time.time() - start_time)
    return jsonify(message)

@app.route('/db')
def db_check():
    start_time = time.time()
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME')
        )
        conn.close()
        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify({"database": "connected"})
    except Exception as e:
        REQUEST_LATENCY.observe(time.time() - start_time)
        return jsonify({"error": str(e)})

# -----------------------------
# PROMETHEUS METRICS ENDPOINT
# -----------------------------
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# -----------------------------
# APP ENTRY POINT
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5000)))
