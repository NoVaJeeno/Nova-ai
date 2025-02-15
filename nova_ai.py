from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import openai
import os
import json
import shutil
import secrets
import requests
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv

# == Sicherheitskonfiguration ==
load_dotenv()  # Falls lokal, lädt .env Datei

# API-Schlüssel aus Environment Variablen abrufen
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ API-Schlüssel nicht gefunden! Stelle sicher, dass OPENAI_API_KEY in den Render Environment Variables gesetzt ist.")

openai.api_key = OPENAI_API_KEY  # Setzt den OpenAI API Key

# == Initialisiere FastAPI ==
app = FastAPI()

# Statische Dateien (für das J.A.R.V.I.S. Design)
app.mount("/static", StaticFiles(directory="static"), name="static")

# == Datenbank-Konfiguration ==
DATABASE_URL = "sqlite:///./nova_ai.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Memory(Base):
    __tablename__ = "memory"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)

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

# == API-Routen ==

@app.get("/")
async def home():
    return {
        "message": "🚀 Nova AI ist jetzt aktiv!",
        "status": "running",
        "design": "J.A.R.V.I.S UI"
    }

@app.post("/chat")
async def chat(input_text: str, db: Session = Depends(get_db)):
    context = recall_memory(db, "chat_history") or ""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": context}, {"role": "user", "content": input_text}],
    )
    reply = response["choices"][0]["message"]["content"]
    store_memory(db, "chat_history", context + "\nUser: " + input_text + "\nNova: " + reply)
    return {"response": reply}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"Datei {file.filename} erfolgreich hochgeladen!", "path": file_location}

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

# == Start der API ==
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)