# WhatsApp AI Bot

A WhatsApp bot that uses **JavaScript (Baileys)** for WhatsApp connection and **Python (FastAPI + OpenRouter AI)** for intelligent responses.

## Architecture

```
User Message -> WhatsApp -> Baileys (JS) -> FastAPI (Python) -> OpenRouter AI -> Reply -> WhatsApp -> User
```

## Prerequisites

- Node.js 18+
- Python 3.10+

## Setup

### 1. Install Node.js Dependencies

```bash
npm install
```

### 2. Setup Python Environment

```bash
cd python
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your OpenRouter API key:

```bash
cp .env.example .env
```

Edit `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
PYTHON_API_URL=http://127.0.0.1:5000
PORT=3000
BOT_PERSONALITY=You are a helpful and friendly WhatsApp assistant.
```

Get your API key from: https://openrouter.ai/keys

## Running the Bot

### Option 1: Run Both Services

**Terminal 1 - Python API:**
```bash
cd python
.venv\Scripts\activate
python main.py
```

**Terminal 2 - JavaScript Bot:**
```bash
npm start
```

### Option 2: Use Batch Script (Windows)

```bash
start.bat
```

## Usage

1. Open http://localhost:3000 in your browser
2. Scan the QR code with WhatsApp (Linked Devices)
3. Bot is now active and will respond to messages

### Knowledge Base Management

Access the knowledge base web interface at: http://localhost:5000/knowledge-ui

You can:
- Add new knowledge entries with title, content, and tags
- Search and filter existing entries
- Edit or delete entries
- View statistics about your knowledge base

## API Endpoints

### JavaScript Server (Port 3000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI with QR code |
| GET | `/qr` | QR code status |
| GET | `/status` | Connection status |
| POST | `/send-message` | Send message manually |

### Python API (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/knowledge-ui` | Knowledge base web interface |
| POST | `/reply` | Get AI response for a message |
| GET | `/conversation/{id}` | Get conversation history |
| DELETE | `/conversation/{id}` | Clear conversation history |
| GET | `/status` | AI service status |
| POST | `/knowledge` | Add knowledge entry |
| GET | `/knowledge` | List all knowledge entries |
| GET | `/knowledge/{id}` | Get specific knowledge entry |
| DELETE | `/knowledge/{id}` | Delete knowledge entry |
| POST | `/knowledge/search` | Search knowledge entries |
| DELETE | `/knowledge` | Clear all knowledge entries |

## Project Structure

```
whatsapp-bot-implemented/
├── index.js                      # Main JavaScript bot (Baileys + Express)
├── package.json                  # Node.js dependencies
├── start.bat                     # Windows startup script
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── public/                       # Static files (QR code images, web UI)
│   └── knowledge.html            # Knowledge base management interface
├── auth_info/                    # WhatsApp session data (gitignored)
├── knowledge_base.json           # Knowledge base storage (gitignored)
├── python/
│   ├── main.py                   # FastAPI server
│   ├── gemini_client.py          # OpenRouter AI integration
│   ├── conversation_manager.py   # Conversation history manager
│   ├── knowledge_base.py         # Knowledge base manager
│   └── requirements.txt          # Python dependencies
└── README.md
```

## Features

- QR code authentication
- Multi-user conversation tracking
- AI-powered responses via OpenRouter (supports multiple models)
- Knowledge base with web management interface
- Conversation history persistence
- REST API for manual messaging
- Web dashboard for monitoring
