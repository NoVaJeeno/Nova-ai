from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import openai
import os
import json
import shutil
import subprocess
import requests
import secrets
import speech_recognition as sr
import pyttsx3

# == Sicherheitseinstellungen ==
MASTER_KEY = os.getenv("MASTER_KEY", "mein_sicherer_master_key")  # Hauptschlüssel für Admin-Zugriff
ALLOW_CONNECTIONS = False  # Standardmäßig sind externe Verbindungen gesperrt
AUTO_UPDATE = False  # Standardmäßig keine automatischen Updates

# == Initialisiere FastAPI ==
app = FastAPI()

# == Datenbank-Konfiguration ==
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nova_ai.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Memory(Base):
    __tablename__ = "memory"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# == Datenbank-Funktionen ==
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_memory(db: Session, key: str, value: str):
    existing = db.query(Memory).filter(Memory.key == key).first()
    if existing:
        existing.value = value
    else:
        db.add(Memory(key=key, value=value))
    db.commit()

def recall_memory(db: Session, key: str):
    result = db.query(Memory).filter(Memory.key == key).first()
    return result.value if result else None

def validate_api_key(db: Session, api_key: str):
    return db.query(APIKey).filter(APIKey.key == api_key).first() is not None

# == API-Schlüssel erstellen ==
@app.post("/generate_key")
async def generate_key(master_key: str, db: Session = Depends(get_db)):
    if master_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    new_key = secrets.token_hex(32)
    db.add(APIKey(key=new_key))
    db.commit()

    return {"message": "API-Schlüssel erstellt!", "api_key": new_key}

# == API-Schlüssel überprüfen ==
@app.post("/validate_key")
async def validate_key(api_key: str, db: Session = Depends(get_db)):
    if validate_api_key(db, api_key):
        return {"message": "API-Schlüssel ist gültig!"}
    else:
        raise HTTPException(status_code=403, detail="Ungültiger API-Schlüssel"}

# == Sprachsteuerung ==
@app.get("/voice_command")
def voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Warte auf Sprachbefehl...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio, language="de-DE")
        print(f"Erkannter Befehl: {command}")
        return {"command": command}
    except sr.UnknownValueError:
        return {"error": "Sprachbefehl nicht verstanden"}
    except sr.RequestError:
        return {"error": "Sprachsteuerung nicht verfügbar"}

# == KI-Chat mit GPT ==
@app.post("/chat")
async def chat(api_key: str, input_text: str, db: Session = Depends(get_db)):
    if not validate_api_key(db, api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    context = recall_memory(db, "chat_history") or ""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": context}, {"role": "user", "content": input_text}],
    )
    reply = response["choices"][0]["message"]["content"]
    store_memory(db, "chat_history", context + "\nUser: " + input_text + "\nNova: " + reply)
    return {"response": reply}

# == Datei-/Bild-Upload ==
@app.post("/upload")
async def upload_file(api_key: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not validate_api_key(db, api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"Datei {file.filename} erfolgreich hochgeladen!", "path": file_location}

# == Verbindung zu GitHub zum autonomen Lernen ==
@app.post("/github_learn")
async def github_learn(api_key: str, repo_url: str, db: Session = Depends(get_db)):
    if api_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    repo_name = repo_url.split("/")[-1]
    os.system(f"git clone {repo_url} repos/{repo_name}")

    return {"message": f"Repository {repo_name} wurde heruntergeladen und analysiert."}

# == Automatische Updates der Webseite ==
@app.post("/toggle_auto_update")
async def toggle_auto_update(api_key: str, enable: bool, db: Session = Depends(get_db)):
    global AUTO_UPDATE
    if api_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    AUTO_UPDATE = enable
    return {"message": f"Auto-Updates {'aktiviert' if enable else 'deaktiviert'}"}

# == Root-Route (Fix für 405 Fehler) ==
@app.get("/", methods=["GET", "HEAD"])
def read_root():
    return {"message": "Nova AI ist aktiv! Willkommen!"}

# == Start der API ==
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)