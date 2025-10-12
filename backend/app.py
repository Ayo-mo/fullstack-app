from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route('/db')
def db_check():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME')
        )
        conn.close()
        return jsonify({"database": "connected"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5000)))
