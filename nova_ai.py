import sqlite3
from flask import Flask, request, jsonify
import logging
from datetime import datetime

# Flask App initialisieren
app = Flask(__name__)

# Logging aktivieren für bessere Fehleranalyse
logging.basicConfig(level=logging.INFO)

# Datenbankverbindung erstellen
DB_FILE = "nova_ai_memory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Chat API Route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Nachricht fehlt"}), 400

    # Simulierter AI-Response
    response = f"Hallo! Du sagtest: {user_message}"

    # Nachricht speichern
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_memory (user_message, ai_response) VALUES (?, ?)", (user_message, response))
    conn.commit()
    conn.close()

    return jsonify({"response": response})

# Admin Panel für Logs und Datenbank Management
@app.route("/admin", methods=["GET"])
def admin_panel():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM chat_memory ORDER BY timestamp DESC LIMIT 10")
    messages = c.fetchall()
    conn.close()
    return jsonify({"last_messages": messages})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)