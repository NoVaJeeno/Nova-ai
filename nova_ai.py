from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import os
import shutil
import requests
import speech_recognition as sr
import pyttsx3
import json
import secrets
from gpt4all import GPT4All
from dotenv import load_dotenv

# == Lade Umgebungsvariablen ==
load_dotenv()

# == Initialisiere GPT4All (Offline KI) ==
llm = GPT4All("ggml-gpt4all-j-v1.3.bin")

# == Sicherheitseinstellungen ==
MASTER_KEY = os.getenv("MASTER_KEY", "mein_sicherer_master_key")

# == Initialisiere FastAPI ==
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

# == Web-Interface ==
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# == Sprachsteuerung (Sprache-zu-Text) ==
@app.get("/voice_command")
def voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio, language="de-DE")
        return {"command": command}
    except sr.UnknownValueError:
        return {"error": "Sprachbefehl nicht verstanden"}
    except sr.RequestError:
        return {"error": "Sprachsteuerung nicht verfügbar"}

# == KI-Chat mit GPT4All ==
@app.post("/chat")
async def chat(input_text: str, db: Session = Depends(get_db)):
    context = recall_memory(db, "chat_history") or ""
    response = llm.generate(context + "\nUser: " + input_text)
    store_memory(db, "chat_history", context + "\nUser: " + input_text + "\nNova: " + response)
    return {"response": response}

# == WLAN-Status überprüfen ==
@app.get("/wifi_status")
def wifi_status():
    try:
        response = os.system("ping -c 1 8.8.8.8")
        return {"status": "Verbunden" if response == 0 else "Nicht verbunden"}
    except Exception as e:
        return {"error": str(e)}

# == Standort abrufen ==
@app.get("/get_location")
def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        location_data = response.json()
        return {
            "Stadt": location_data["city"],
            "Land": location_data["country"],
            "IP": location_data["query"]
        }
    except Exception as e:
        return {"error": str(e)}

# == Start der API ==
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)