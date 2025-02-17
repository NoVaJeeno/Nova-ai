import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

# Flask App initialisieren
app = Flask(__name__)
CORS(app)  # Erlaubt externe API-Zugriffe

# Logging aktivieren
logging.basicConfig(level=logging.INFO)

# Datenbank für Speicherfunktion
DB_FILE = "/data/nova_ai_memory.db" if os.getenv("RENDER") else "nova_ai_memory.db"

def init_db():
    """Erstellt die SQLite-Datenbank und die Tabelle, falls sie nicht existiert."""
    try:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    except Exception as e:
        logging.warning(f"Konnte Datenbankverzeichnis nicht erstellen: {e}")

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
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO chat_memory (user_message, ai_response) VALUES (?, ?)", (user_message, response))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Fehler beim Speichern: {e}")
        return jsonify({"error": "Datenbankfehler"}), 500

    return jsonify({"response": response})

# Admin Panel für Logs und Datenbank Management
@app.route("/admin", methods=["GET"])
def admin_panel():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM chat_memory ORDER BY timestamp DESC LIMIT 10")
        messages = c.fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Daten: {e}")
        return jsonify({"error": "Datenbankfehler"}), 500

    return jsonify({"last_messages": messages})

# Startet die Flask-App mit Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)