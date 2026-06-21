import logging
import os

from openai import AsyncOpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(env_path)

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found. Set it in .env file.")

        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_name = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b:free")

    async def generate_response(self, sender_id: str, message: str, personality: str, history: list, knowledge_context: str = "") -> str:
        try:
            system_prompt = f"""{personality}

You are responding to WhatsApp messages. Keep your responses:
- Concise and natural
- Friendly and helpful
- Contextually relevant based on conversation history
- Use simple formatting (avoid complex markdown)

IMPORTANT: ALWAYS respond in the SAME LANGUAGE as the user's message.
- If the user writes in French, respond in French
- If the user writes in Arabic, respond in Arabic
- If the user writes in English, respond in English
- Match the user's language exactly

Respond directly to the user's latest message."""

            if knowledge_context:
                system_prompt += f"""

IMPORTANT - KNOWLEDGE BASE (use this as your PRIMARY source of truth):
{knowledge_context}

RULES:
1. ALWAYS prioritize the knowledge base above your general knowledge
2. If the knowledge base contains information about the user's question, answer using ONLY that information
3. Do NOT say "I'm not familiar with" if the knowledge base covers the topic
4. Keep responses concise and natural for WhatsApp
5. If the knowledge base doesn't cover the topic, then use your general knowledge"""

            messages = [{"role": "system", "content": system_prompt}]

            for msg in history[-20:]:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})

            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenRouter API error: %s", e)
            return "I apologize, but I'm having trouble processing your message right now. Please try again later."
