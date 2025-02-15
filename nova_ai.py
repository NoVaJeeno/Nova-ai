from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import uvicorn
import os
import openai

# == Initialisiere FastAPI ==
app = FastAPI()

# == Datenbank-Konfiguration ==
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nova.db")  # Nutzt PostgreSQL oder SQLite
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# == Datenbank-Modell ==
class DataEntry(Base):
    __tablename__ = "data_entries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    content = Column(Text)

Base.metadata.create_all(bind=engine)

# == OpenAI Schlüssel (muss in Environment Variablen gesetzt werden) ==
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# == Startseite ==
@app.get("/")
def home():
    return {"message": "🚀 Nova AI ist aktiv und bereit zum Lernen!"}

# == 1. API zum Hochladen & Speichern von Dateien ==
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"./uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"message": f"Datei '{file.filename}' wurde hochgeladen und gespeichert!"}

# == 2. API zum Speichern & Abrufen von Daten aus der Datenbank ==
@app.post("/save/")
def save_data(name: str, content: str):
    db = SessionLocal()
    db_entry = DataEntry(name=name, content=content)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.close()
    return {"message": f"Eintrag '{name}' gespeichert!"}

@app.get("/data/{name}")
def get_data(name: str):
    db = SessionLocal()
    entry = db.query(DataEntry).filter(DataEntry.name == name).first()
    db.close()
    if entry:
        return {"name": entry.name, "content": entry.content}
    else:
        raise HTTPException(status_code=404, detail="Daten nicht gefunden")

# == 3. API zur Generierung von Code für Apps ==
@app.post("/generate_code/")
def generate_code(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Erstelle eine App basierend auf: {prompt}"}]
    )
    return {"generated_code": response["choices"][0]["message"]["content"]}

# == 4. API zur Spracherkennung & Steuerung ==
@app.post("/voice_command/")
def voice_command(command: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Verarbeite Sprachbefehl: {command}"}]
    )
    return {"response": response["choices"][0]["message"]["content"]}

# == 5. API zur Weiterentwicklung von Nova AI ==
@app.post("/self_learn/")
def self_learn(topic: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Lerne über: {topic}"}]
    )
    return {"learning_result": response["choices"][0]["message"]["content"]}

# == Starte Uvicorn-Server ==
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
    from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# FastAPI App
app = FastAPI()

# Datenbankverbindung
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nova_ai.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Datenmodell für Wissen
class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True)
    answer = Column(String)

# Datenbank erstellen
Base.metadata.create_all(bind=engine)

# Datenbank-Sitzung erhalten
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
