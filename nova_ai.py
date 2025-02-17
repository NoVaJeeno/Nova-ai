import os
import sqlite3
import json
import zipfile
import subprocess
import shutil
import requests
from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
from gpt4all import GPT4All  # Open-Source KI-Modelle

# Flask App initialisieren
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
GITHUB_REPO = "https://github.com/DEIN_GITHUB_REPO"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Logging aktivieren
logging.basicConfig(level=logging.INFO)

# Datenbankdatei
DB_FILE = "nova_ai_memory.db"

# Datenbank initialisieren
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Open-Source KI-Modell laden (GPT4All oder LLaMA.cpp)
def load_ai_model():
    try:
        model = GPT4All("ggml-gpt4all-j.bin")
        return model
    except Exception:
        return None

ai_model = load_ai_model()

# KI-Logik mit Lernen
def get_ai_response(message):
    """Holt eine Antwort von Open-Source-KI"""
    if ai_model:
        response = ai_model.generate(message)
        return response
    else:
        save_knowledge(message)
        return f"Ich habe die Information gespeichert: {message}"

# Wissen speichern
def save_knowledge(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO knowledge_base (data) VALUES (?)", (data,))
    conn.commit()
    conn.close()

# ZIP-Datei analysieren
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400

    file = request.files["file"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    if file.filename.endswith(".zip"):
        extract_path = os.path.join(app.config["UPLOAD_FOLDER"], "unzipped")
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        return jsonify({"message": "ZIP-Datei entpackt und analysiert"}), 200

    return jsonify({"message": f"Datei {file.filename} gespeichert"}), 200

# Automatisches Code-Update über GitHub
@app.route("/update", methods=["POST"])
def update_code():
    os.system(f"git pull {GITHUB_REPO}")
    os.system("pip install -r requirements.txt")
    return jsonify({"message": "Code aktualisiert!"}), 200

# KI-Chat Route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Nachricht fehlt"}), 400

    response = get_ai_response(user_message)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_memory (user_message, ai_response) VALUES (?, ?)", (user_message, response))
    conn.commit()
    conn.close()

    return jsonify({"response": response})

# Webinterface
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)