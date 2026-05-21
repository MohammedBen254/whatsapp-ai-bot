# 🤖 WhatsApp AI Bot

> A powerful, intelligent WhatsApp bot powered by **Baileys** and **OpenRouter AI** with a dual-stack architecture (Node.js + Python FastAPI).

[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Baileys](https://img.shields.io/badge/Baileys-v6.7.9-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://github.com/WhiskeySockets/Baileys)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## ✨ Features

- 🔐 **QR Code Authentication** — Scan to link your WhatsApp account instantly
- 🧠 **AI-Powered Responses** — Leverages OpenRouter AI with support for multiple LLM models
- 💬 **Multi-User Conversation Tracking** — Maintains context per user with persistent history
- 📚 **Knowledge Base System** — Add, search, and manage custom knowledge entries via web UI
- 🌐 **REST API** — Full API for manual messaging, conversation management, and knowledge CRUD
- 📊 **Web Dashboard** — Monitor bot status, view QR code, and manage knowledge base from browser
- 🔄 **Auto-Reconnect** — Handles disconnections gracefully with automatic reconnection

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│   WhatsApp   │────▶│  Baileys (JS)    │────▶│  FastAPI (Python)│────▶│  OpenRouter  │
│   Client     │◀────│  Express Server  │◀────│  AI Backend      │◀────│  AI Models   │
└─────────────┘     └──────────────────┘     └──────────────────┘     └──────────────┘
                           │                          │
                           ▼                          ▼
                    ┌──────────────┐          ┌──────────────────┐
                    │  QR Code UI  │          │  Knowledge Base  │
                    │  (Port 3000) │          │  (Port 5000)     │
                    └──────────────┘          └──────────────────┘
```

---

## 📋 Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js     | 18+     |
| Python      | 3.10+   |
| npm         | Latest  |
| pip         | Latest  |

---

## 🚀 Quick Start

### 1️⃣ Clone & Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Setup Python virtual environment
cd python
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac

# Install Python packages
pip install -r requirements.txt
cd ..
```

### 2️⃣ Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Python API configuration
PYTHON_API_URL=http://127.0.0.1:5000

# Server configuration
PORT=3000

# OpenRouter API Key (Get yours: https://openrouter.ai/keys)
OPENROUTER_API_KEY=your_openrouter_api_key

# Bot personality
BOT_PERSONALITY=You are a helpful and friendly WhatsApp assistant.

# Knowledge Base
KNOWLEDGE_BASE_ENABLED=true
```

### 3️⃣ Run the Bot

**Option A: Run Both Services Manually**

```bash
# Terminal 1 — Python API Server
cd python
.venv\Scripts\activate
python main.py

# Terminal 2 — WhatsApp Bot
npm start
```

**Option B: Windows One-Click Start**

```bash
start.bat
```

### 4️⃣ Connect & Go

1. Open **http://localhost:3000** in your browser
2. Scan the QR code with WhatsApp (**Linked Devices**)
3. Bot is now active and responding to messages!

---

## 📡 API Endpoints

### JavaScript Server (Port 3000)

| Method | Endpoint         | Description              |
|--------|------------------|--------------------------|
| `GET`  | `/`              | Web UI with QR code      |
| `GET`  | `/qr`            | QR code status (JSON)    |
| `GET`  | `/status`        | Connection status        |
| `POST` | `/send-message`  | Send message manually    |

### Python API (Port 5000)

| Method   | Endpoint                      | Description                    |
|----------|-------------------------------|--------------------------------|
| `GET`    | `/`                           | API status                     |
| `GET`    | `/knowledge-ui`               | Knowledge base web interface   |
| `POST`   | `/reply`                      | Get AI response for a message  |
| `GET`    | `/conversation/{id}`          | Get conversation history       |
| `DELETE` | `/conversation/{id}`          | Clear conversation history     |
| `GET`    | `/status`                     | AI service status              |
| `POST`   | `/knowledge`                  | Add knowledge entry            |
| `GET`    | `/knowledge`                  | List all knowledge entries     |
| `GET`    | `/knowledge/{id}`             | Get specific knowledge entry   |
| `DELETE` | `/knowledge/{id}`             | Delete knowledge entry         |
| `POST`   | `/knowledge/search`           | Search knowledge entries       |
| `DELETE` | `/knowledge`                  | Clear all knowledge entries    |

---

## 📁 Project Structure

```
whatsapp-bot-implemented/
├── index.js                      # Main bot (Baileys + Express)
├── package.json                  # Node.js dependencies & scripts
├── start.bat                     # Windows startup script
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── public/                       # Static files & web UI
│   └── knowledge.html            # Knowledge base management interface
├── auth_info/                    # WhatsApp session data (gitignored)
├── knowledge_base.json           # Knowledge base storage (gitignored)
├── conversations.json            # Conversation history (gitignored)
├── python/
│   ├── main.py                   # FastAPI server & routes
│   ├── gemini_client.py          # OpenRouter AI integration
│   ├── conversation_manager.py   # Conversation history manager
│   ├── knowledge_base.py         # Knowledge base manager
│   └── requirements.txt          # Python dependencies
└── README.md                     # You are here
```

---

## 🛠️ Development

### Available Scripts

```bash
npm start       # Start the bot in production mode
npm run dev     # Start with auto-reload (nodemon)
```

### Knowledge Base Management

Access the knowledge base web interface at: **http://localhost:5000/knowledge-ui**

- ➕ Add new knowledge entries with title, content, and tags
- 🔍 Search and filter existing entries
- ✏️ Edit or delete entries
- 📊 View statistics about your knowledge base

---

## 🔧 Troubleshooting

| Issue                        | Solution                                              |
|------------------------------|-------------------------------------------------------|
| QR code not showing          | Ensure port 3000 is not in use, restart the bot       |
| AI not responding            | Verify `OPENROUTER_API_KEY` is set correctly          |
| Python API not reachable     | Check if Python server is running on port 5000        |
| Session lost on restart      | `auth_info/` folder persists sessions automatically   |

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">Built with ❤️ using Baileys, FastAPI & OpenRouter AI</p>
