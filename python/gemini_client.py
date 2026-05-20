import os
from openai import AsyncOpenAI
from dotenv import load_dotenv


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
        self.model_name = "nvidia/nemotron-3-super-120b-a12b:free"
        self.chat_sessions = {}

    async def generate_response(self, sender_id: str, message: str, personality: str, history: list) -> str:
        try:
            system_prompt = f"""{personality}

You are responding to WhatsApp messages. Keep your responses:
- Concise and natural
- Friendly and helpful
- Contextually relevant based on conversation history
- Use simple formatting (avoid complex markdown)

Respond directly to the user's latest message."""

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
            print(f"OpenRouter API error: {e}")
            return "I apologize, but I'm having trouble processing your message right now. Please try again later."
