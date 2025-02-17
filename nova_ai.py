import os
import sqlite3
import json
import zipfile
import subprocess
import shutil
import requests
import logging
import time
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from gpt4all import GPT4All  # Open-Source KI-Modelle

# Flask App initialisieren
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
GITHUB_REPO = "https://github.com/DEIN_GITHUB_REPO"
MODEL_DIR = "models"
MODEL_FILE = "ggml-gpt4all-j.bin"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
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

# Open-Source KI-Modell laden (GPT4All oder Alternative)
def load_ai_model():
    if not os.path.exists(MODEL_PATH):
        logging.info("Lade das KI-Modell herunter...")
        model_url = "https://gpt4all.io/models/ggml-gpt4all-j.bin"
        
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            with open(MODEL_PATH, "wb") as model_file:
                for chunk in response.iter_content(chunk_size=1024):
                    model_file.write(chunk)
            logging.info("Modell erfolgreich heruntergeladen.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler beim Herunterladen des KI-Modells: {e}")
            return None

    try:
        model = GPT4All(MODEL_PATH)
        return model
    except Exception as e:
        logging.error(f"Fehler beim Laden des KI-Modells: {e}")
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

# WLAN-Zugriff erlauben (nur auf Befehl des Admins)
@app.route("/wifi_access", methods=["POST"])
def wifi_access():
    data = request.get_json()
    allow_access = data.get("allow")

    if allow_access:
        logging.info("WLAN-Zugriff wurde gewährt.")
        return jsonify({"message": "WLAN-Zugriff erlaubt."}), 200
    else:
        return jsonify({"message": "Zugriff verweigert."}), 403

# Sprachausgabe-Funktion
@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "Kein Text für Sprachausgabe erhalten"}), 400

    try:
        subprocess.run(["say", text])  # Funktioniert auf macOS
        return jsonify({"message": "Text gesprochen"}), 200
    except Exception as e:
        return jsonify({"error": f"Sprachausgabe fehlgeschlagen: {str(e)}"}), 500

# Automatische Architektur-Generierung
@app.route("/generate_architecture", methods=["POST"])
def generate_architecture():
    try:
        arch_script = """
        import json

        architecture = {
            "services": ["Webserver", "Datenbank", "KI-Modell"],
            "connections": ["API-Calls", "Datenfluss"]
        }

        with open("architecture.json", "w") as f:
            json.dump(architecture, f)

        print("Architektur-Datei erstellt!")
        """

        with open("generate_arch.py", "w") as f:
            f.write(arch_script)

        subprocess.run(["python", "generate_arch.py"])
        return jsonify({"message": "Architektur generiert"}), 200
    except Exception as e:
        return jsonify({"error": f"Fehler bei der Architektur-Generierung: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)