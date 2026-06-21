import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, storage_file=None):
        if storage_file is None:
            storage_file = os.path.join(os.path.dirname(__file__), '..', 'conversations.json')
        self.storage_file = storage_file
        self.conversations = self._load()

    def _load(self):
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error("Error loading conversations: %s", e)
        return {}

    def _save(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error saving conversations: %s", e)

    def add_message(self, sender_id: str, role: str, content: str):
        if sender_id not in self.conversations:
            self.conversations[sender_id] = {
                "sender_id": sender_id,
                "messages": [],
                "created_at": datetime.utcnow().isoformat(),
                "last_message_at": datetime.utcnow().isoformat()
            }

        self.conversations[sender_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.conversations[sender_id]["last_message_at"] = datetime.utcnow().isoformat()

        if len(self.conversations[sender_id]["messages"]) > 50:
            self.conversations[sender_id]["messages"] = self.conversations[sender_id]["messages"][-50:]

        self._save()

    def get_history(self, sender_id: str, limit: int = None):
        if sender_id not in self.conversations:
            return []

        messages = self.conversations[sender_id]["messages"]
        if limit:
            return messages[-limit:]
        return messages

    def clear_history(self, sender_id: str):
        if sender_id in self.conversations:
            del self.conversations[sender_id]
            self._save()

    def get_total_conversations(self):
        return len(self.conversations)

    def get_all_summaries(self):
        summaries = []
        for sender_id, conv in self.conversations.items():
            messages = conv["messages"]
            summaries.append({
                "sender_id": sender_id,
                "message_count": len(messages),
                "created_at": conv["created_at"],
                "last_message_at": conv["last_message_at"],
                "last_message": messages[-1] if messages else None
            })
        return summaries
