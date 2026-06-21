from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from gemini_client import GeminiClient
from conversation_manager import ConversationManager
from knowledge_base import KnowledgeBase
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp AI API")

gemini = GeminiClient()
conversations = ConversationManager()
knowledge_base = KnowledgeBase()

static_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class MessageRequest(BaseModel):
    from_: str = Field(alias="from")
    message: str
    personality: str = "You are a helpful WhatsApp assistant."


class MessageResponse(BaseModel):
    reply: str


class KnowledgeEntryRequest(BaseModel):
    title: str
    content: str
    tags: list[str] = []


class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5


@app.get("/")
async def root():
    return {"status": "ok", "endpoints": ["POST /reply"]}


@app.get("/knowledge-ui")
async def knowledge_ui():
    kb_path = os.path.join(static_dir, 'knowledge.html')
    if os.path.exists(kb_path):
        return FileResponse(kb_path)
    return HTMLResponse(content="<h1>Knowledge UI not found</h1>", status_code=404)


@app.post("/reply", response_model=MessageResponse)
async def reply(request: MessageRequest):
    sender = request.from_
    user_message = request.message.strip()

    if not user_message:
        return MessageResponse(reply="I received an empty message.")

    history = conversations.get_history(sender)
    knowledge_context = knowledge_base.get_relevant_context(user_message)

    try:
        ai_response = await gemini.generate_response(
            sender_id=sender,
            message=user_message,
            personality=request.personality,
            history=history,
            knowledge_context=knowledge_context
        )

        conversations.add_message(sender, "user", user_message)
        conversations.add_message(sender, "assistant", ai_response)

        return MessageResponse(reply=ai_response)
    except Exception as e:
        logger.error("Error generating response: %s", e)
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
        "total_conversations": conversations.get_total_conversations(),
        "knowledge_base_entries": knowledge_base.get_entry_count()
    }


@app.post("/knowledge")
async def add_knowledge_entry(request: KnowledgeEntryRequest):
    entry = knowledge_base.add_entry(
        title=request.title,
        content=request.content,
        tags=request.tags
    )
    return {"success": True, "entry": entry}


@app.get("/knowledge")
async def get_knowledge_entries():
    return {"entries": knowledge_base.get_all_entries(), "count": knowledge_base.get_entry_count()}


@app.get("/knowledge/{entry_id}")
async def get_knowledge_entry(entry_id: int):
    entry = knowledge_base.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"entry": entry}


@app.delete("/knowledge/{entry_id}")
async def delete_knowledge_entry(entry_id: int):
    success = knowledge_base.remove_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True, "message": f"Entry {entry_id} deleted"}


@app.post("/knowledge/search")
async def search_knowledge(request: KnowledgeSearchRequest):
    results = knowledge_base.search_entries(request.query, limit=request.limit)
    return {"query": request.query, "results": results, "count": len(results)}


@app.delete("/knowledge")
async def clear_knowledge_base():
    knowledge_base.clear_all()
    return {"success": True, "message": "Knowledge base cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
