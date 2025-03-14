from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.service import chatbot_service


router = APIRouter()

class ChatbotInput(BaseModel):
    query: str

@router.post("/ask")
async def ask_chatbot(input_data: ChatbotInput):
    try:
        response = chatbot_service.get_response(input_data.query)
        return {"response": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat_history")
async def get_chat_history():
    chat_history = chatbot_service.get_chat_history()
    return {"chat_history": chat_history}