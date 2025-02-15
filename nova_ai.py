from fastapi import FastAPI
import uvicorn
import platform
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "🚀 Nova AI ist jetzt aktiv!"}

@app.get("/info")
def get_info():
    return {
        "app_name": "Nova AI",
        "version": "1.0",
        "system": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
    }

@app.post("/predict")
def predict(data: dict):
    """
    Diese Route ist ein Platzhalter für zukünftige KI-Modelle.
    Sie kann für Sprachverarbeitung, Bilderkennung oder andere AI-Tasks genutzt werden.
    """
    logger.info(f"Received data: {data}")
    return {"prediction": "Hier könnte deine AI-Vorhersage stehen!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)