from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import shutil
import zipfile
import bluetooth
import wifi

# Initialisiere FastAPI
app = FastAPI()

# == Datenbank-Konfiguration ==
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nova_ai.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True)
    answer = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# == Chat-Funktion mit Lernen ==
class Message(BaseModel):
    text: str

@app.post("/chat/")
async def chat(message: Message, db=Depends(get_db)):
    user_input = message.text.lower()
    existing_knowledge = db.query(Knowledge).filter(Knowledge.question == user_input).first()
    if existing_knowledge:
        return {"message": existing_knowledge.answer}
    new_answer = f"Ich weiß noch nicht viel über '{message.text}', kannst du mir mehr sagen?"
    new_entry = Knowledge(question=user_input, answer=new_answer)
    db.add(new_entry)
    db.commit()
    return {"message": new_answer}

class LearnData(BaseModel):
    question: str
    answer: str

@app.post("/learn/")
async def learn(data: LearnData, db=Depends(get_db)):
    existing_entry = db.query(Knowledge).filter(Knowledge.question == data.question.lower()).first()
    if existing_entry:
        existing_entry.answer = data.answer
    else:
        new_entry = Knowledge(question=data.question.lower(), answer=data.answer)
        db.add(new_entry)
    db.commit()
    return {"message": "Nova AI hat dazugelernt!"}

# == Datei-Upload (ZIP und andere Formate) ==
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Falls es ein ZIP-Archiv ist, entpacken
    if file.filename.endswith(".zip"):
        with zipfile.ZipFile(file_location, 'r') as zip_ref:
            zip_ref.extractall(UPLOAD_FOLDER)
        return {"message": f"ZIP-Datei {file.filename} wurde entpackt!"}
    
    return {"message": f"Datei {file.filename} hochgeladen!"}

# == Bluetooth-Geräte scannen ==
@app.get("/bluetooth/")
async def scan_bluetooth():
    devices = bluetooth.discover_devices(duration=5, lookup_names=True)
    return {"devices": [{"name": name, "address": addr} for addr, name in devices]}

# == WLAN-Netzwerke scannen ==
@app.get("/wifi/")
async def scan_wifi():
    networks = wifi.Cell.all('wlan0')  # Falls nötig, 'wlan0' anpassen
    return {"networks": [{"ssid": net.ssid, "signal": net.signal} for net in networks]}