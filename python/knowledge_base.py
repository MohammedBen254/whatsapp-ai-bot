import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, storage_file=None):
        if storage_file is None:
            storage_file = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base.json')
        self.storage_file = storage_file
        self.entries = self._load()

    def _load(self):
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error("Error loading knowledge base: %s", e)
        return {"entries": []}

    def _save(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error saving knowledge base: %s", e)

    def add_entry(self, title: str, content: str, tags: list = None) -> dict:
        entry = {
            "id": len(self.entries["entries"]) + 1,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.entries["entries"].append(entry)
        self._save()
        return entry

    def remove_entry(self, entry_id: int) -> bool:
        for i, entry in enumerate(self.entries["entries"]):
            if entry["id"] == entry_id:
                del self.entries["entries"][i]
                self._save()
                return True
        return False

    def get_entry(self, entry_id: int) -> dict | None:
        for entry in self.entries["entries"]:
            if entry["id"] == entry_id:
                return entry
        return None

    def get_all_entries(self) -> list:
        return self.entries["entries"]

    def search_entries(self, query: str, limit: int = 5) -> list:
        query_lower = query.lower()
        keywords = [k for k in query_lower.split() if len(k) > 2]
        scored = []

        for entry in self.entries["entries"]:
            score = 0
            title_lower = entry["title"].lower()
            content_lower = entry["content"].lower()
            tags_lower = [t.lower() for t in entry.get("tags", [])]

            if query_lower in title_lower:
                score += 20
            if query_lower in content_lower:
                score += 10

            for keyword in keywords:
                if keyword in title_lower:
                    score += 10
                if keyword in content_lower:
                    score += 2
                for tag in tags_lower:
                    if keyword in tag:
                        score += 5

            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def get_relevant_context(self, query: str, max_entries: int = 3) -> str:
        relevant = self.search_entries(query, limit=max_entries)
        if not relevant:
            entries = self.entries["entries"]
            if entries:
                relevant = entries[:max_entries]

        if not relevant:
            return ""

        context_parts = []
        for entry in relevant:
            context_parts.append(f"Title: {entry['title']}\nContent: {entry['content']}")

        return "\n\n---\n\n".join(context_parts)

    def clear_all(self):
        self.entries = {"entries": []}
        self._save()

    def get_entry_count(self):
        return len(self.entries["entries"])
