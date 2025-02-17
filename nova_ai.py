from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os
import openai
from gpt4all import GPT4All
from llama_cpp import Llama
from fastapi.staticfiles import StaticFiles

# 📂 Datenbank einrichten
DB_FILE = "database/memory.db"

def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 📂 FastAPI-Server starten
app = FastAPI()

# 📂 Statische Dateien (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

# 🤖 KI-Modelle automatisch laden
GPT4ALL_MODEL = "gpt4all-falcon-q4_0.gguf"
LLAMA_MODEL = "llama-7b.gguf"

gpt_model = GPT4All(GPT4ALL_MODEL) if os.path.exists(GPT4ALL_MODEL) else None
llama_model = Llama(model_path=LLAMA_MODEL) if os.path.exists(LLAMA_MODEL) else None
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

def call_ai(prompt):
    """Wählt automatisch eine verfügbare KI."""
    if gpt_model:
        response = gpt_model.generate(prompt)
    elif llama_model:
        response = llama_model(prompt)
    elif openai.api_key:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )['choices'][0]['message']['content']
    else:
        response = "❌ Keine funktionierende KI verfügbar."

    # Speicher das Gespräch in die Datenbank
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_memory (user_message, ai_response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()

    return response

@app.post("/chat")
async def chat(request: ChatRequest):
    response = call_ai(request.message)
    return {"response": response}

@app.get("/")
async def home():
    return HTMLResponse(open("templates/index.html").read())

@app.get("/memory")
async def get_memory():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_memory ORDER BY id DESC LIMIT 10")
    history = cursor.fetchall()
    conn.close()
    return {"history": history}