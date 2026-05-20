from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from gemini_client import GeminiClient
from conversation_manager import ConversationManager
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="WhatsApp AI API")

gemini = GeminiClient()
conversations = ConversationManager()


class MessageRequest(BaseModel):
    from_: str = Field(alias="from")
    message: str
    personality: str = "You are a helpful WhatsApp assistant."


class MessageResponse(BaseModel):
    reply: str


@app.get("/")
async def root():
    return {"status": "ok", "endpoints": ["POST /reply"]}


@app.post("/reply", response_model=MessageResponse)
async def reply(request: MessageRequest):
    sender = request.from_
    user_message = request.message.strip()

    if not user_message:
        return MessageResponse(reply="I received an empty message.")

    history = conversations.get_history(sender)

    try:
        ai_response = await gemini.generate_response(
            sender_id=sender,
            message=user_message,
            personality=request.personality,
            history=history
        )

        conversations.add_message(sender, "user", user_message)
        conversations.add_message(sender, "assistant", ai_response)

        return MessageResponse(reply=ai_response)
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return MessageResponse(reply="Sorry, I am having trouble processing your message. Please try again later.")


@app.get("/conversation/{sender_id}")
async def get_conversation(sender_id: str, limit: int = 50):
    history = conversations.get_history(sender_id, limit=limit)
    return {"sender_id": sender_id, "message_count": len(history), "history": history}


@app.delete("/conversation/{sender_id}")
async def clear_conversation(sender_id: str):
    conversations.clear_history(sender_id)
    return {"success": True, "message": f"Conversation cleared for {sender_id}"}


@app.get("/status")
async def status():
    return {
        "ai_enabled": True,
        "total_conversations": conversations.get_total_conversations()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
