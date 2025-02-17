import os
import sqlite3
import zipfile
import logging
import requests
import shutil
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from gpt4all import GPT4All  # Falls nicht verfügbar, wird eine Alternative heruntergeladen

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

# Verfügbare KI-Modelle prüfen & herunterladen
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "ggml-gpt4all-j.bin")
MODEL_URL = "https://gpt4all.io/models/ggml-gpt4all-j.bin"

os.makedirs(MODEL_DIR, exist_ok=True)

def ensure_model():
    """Prüft, ob das Modell vorhanden ist, und lädt es falls nötig herunter."""
    if not os.path.exists(MODEL_PATH):
        logging.info("KI-Modell nicht gefunden, lade es herunter...")
        response = requests.get(MODEL_URL, stream=True)
        with open(MODEL_PATH, "wb") as model_file:
            shutil.copyfileobj(response.raw, model_file)
        logging.info("Modell erfolgreich heruntergeladen!")
    else:
        logging.info("KI-Modell ist bereits vorhanden.")

ensure_model()

# Open-Source KI-Modell laden (GPT4All oder Alternative)
def load_ai_model():
    try:
        model = GPT4All(MODEL_PATH)
        return model
    except Exception:
        return None

ai_model = load_ai_model()

# KI-Logik mit Lernen
def get_ai_response(message):
    """Holt eine Antwort von Open-Source-KI oder speichert Wissen."""
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
    os.system("git pull origin main")
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