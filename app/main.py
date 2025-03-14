from fastapi import FastAPI
from app.api.v1.endpoints import chatbot

app = FastAPI(title="Chatbot API")

# Include chatbot endpoints
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])

@app.get("/")
def health_check():
    return {"message": "Chatbot API is running!!"}