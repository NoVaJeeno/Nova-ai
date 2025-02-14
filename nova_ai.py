from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "🚀 Nova AI ist jetzt aktiv!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)