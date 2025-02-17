import os
import sqlite3
import json
import zipfile
import shutil
import requests
from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
from gpt4all import GPT4All

# Flask App initialisieren
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
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
    conn.commit()
    conn.close()

init_db()

# Open-Source KI-Modell laden mit automatischer Auswahl
def load_ai_model():
    model_list = [
        "models/ggml-gpt4all-j.bin",
        "models/ggml-mistral.bin",
        "models/ggml-llama2.bin"
    ]
    
    for model_path in model_list:
        if os.path.exists(model_path):
            logging.info(f"🔄 Lade Modell: {model_path}")
            return GPT4All(model_path)

    logging.warning("⚠️ Kein Modell gefunden, versuche Download...")
    download_model("models/ggml-gpt4all-j.bin")
    return GPT4All("models/ggml-gpt4all-j.bin") if os.path.exists("models/ggml-gpt4all-j.bin") else None

def download_model(model_path):
    url = "https://gpt4all.io/models/ggml-gpt4all-j.bin"
    os.makedirs("models", exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(model_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        logging.info("✅ Modell erfolgreich heruntergeladen!")
    else:
        logging.error("❌ Fehler beim Herunterladen des Modells!")

ai_model = load_ai_model()

# KI-Logik mit Antworten
def get_ai_response(message):
    """Holt eine Antwort von Open-Source-KI"""
    if ai_model:
        response = ai_model.generate(message)
        return response
    else:
        return f"❌ KI-Modell konnte nicht geladen werden. Nachricht gespeichert: {message}"

# ZIP-Dateien analysieren
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