import * as baileys from '@whiskeysockets/baileys'
import { Boom } from '@hapi/boom'
import fetch from 'node-fetch'
import fs from 'fs'
import express from 'express'
import path from 'path'
import QRCode from 'qrcode'
import cors from 'cors'
import dotenv from 'dotenv'

dotenv.config()

const AUTH_DIR = './auth_info'
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://127.0.0.1:5000'
const BOT_PERSONALITY = process.env.BOT_PERSONALITY || 'You are a helpful WhatsApp assistant.'

if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true })
}

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = baileys

const app = express()
app.use(cors())
app.use(express.json())

const publicDir = path.join(process.cwd(), 'public')
if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true })
}
app.use(express.static(publicDir))

let currentQR = null
let isConnected = false
let sock = null

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR)

    const { version, isLatest } = await fetchLatestBaileysVersion()
    console.log(`Using Baileys version: ${version.join('.')}`)

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        browser: ['Ubuntu', 'Chrome', '20.0.04']
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update

        if (qr) {
            try {
                const qrBuffer = await QRCode.toBuffer(qr, { type: 'png', scale: 6 })
                const qrPath = path.join(publicDir, 'qr.png')
                fs.writeFileSync(qrPath, qrBuffer)
                currentQR = '/qr.png'
                console.log('QR Code generated and saved to public/qr.png')
            } catch (err) {
                console.error('QR generation error:', err.message)
            }
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error instanceof Boom ? lastDisconnect.error.output.statusCode : null
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut

            console.log('Connection closed. Reason:', lastDisconnect?.error?.message)
            isConnected = false

            if (shouldReconnect) {
                console.log('Reconnecting...')
                setTimeout(() => connectToWhatsApp(), 3000)
            }
        } else if (connection === 'open') {
            console.log('WhatsApp connected successfully!')
            isConnected = true
            currentQR = null
        }
    })

    sock.ev.on('messages.upsert', async (m) => {
        try {
            const messages = m.messages || []
            for (const msg of messages) {
                if (!msg.message || msg.key.fromMe) continue

                const jid = msg.key.remoteJid
                if (jid.includes('@g.us')) continue

                const text = msg.message.conversation || msg.message?.extendedTextMessage?.text || ''
                if (!text || text.trim() === '') continue

                console.log(`Message from ${jid}: ${text}`)

                try {
                    const response = await fetch(`${PYTHON_API_URL}/reply`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            from: jid,
                            message: text,
                            personality: BOT_PERSONALITY
                        })
                    })

                    const data = await response.json()
                    if (data && data.reply) {
                        await sock.sendMessage(jid, { text: data.reply })
                        console.log(`Replied to ${jid}: ${data.reply}`)
                    }
                } catch (err) {
                    console.error('Failed to get AI response:', err.message)
                    await sock.sendMessage(jid, { text: 'Sorry, I am having trouble processing your message right now. Please try again later.' })
                }
            }
        } catch (err) {
            console.error('Message handler error:', err)
        }
    })
}

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>WhatsApp Bot</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: linear-gradient(135deg, #25D366, #128C7E); }
                .container { text-align: center; background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 500px; }
                h1 { color: #333; margin-bottom: 1rem; }
                .status { font-size: 1.2em; margin: 1rem 0; }
                .connected { color: #25D366; }
                .disconnected { color: #ff6b6b; }
                img { max-width: 300px; margin: 1rem 0; }
                button { background: #25D366; color: white; border: none; padding: 12px 30px; border-radius: 25px; font-size: 1em; cursor: pointer; margin-top: 1rem; }
                button:hover { background: #128C7E; }
            </style>
            <script>
                setInterval(() => location.reload(), 5000);
            </script>
        </head>
        <body>
            <div class="container">
                <h1>WhatsApp AI Bot</h1>
                ${isConnected
                    ? '<div class="status connected">Connected</div><p>Bot is active and responding to messages.</p>'
                    : currentQR
                        ? '<div class="status disconnected">Scan QR to connect</div><img src="' + currentQR + '" alt="QR Code">'
                        : '<div class="status disconnected">Initializing...</div><p>Please wait...</p>'
                }
                <button onclick="location.reload()">Refresh</button>
            </div>
        </body>
        </html>
    `)
})

app.get('/qr', (req, res) => {
    if (isConnected) {
        return res.json({ status: 'connected' })
    }
    if (currentQR) {
        return res.json({ status: 'qr_available', qr: currentQR })
    }
    res.json({ status: 'waiting' })
})

app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        status: isConnected ? 'Connected' : 'Disconnected'
    })
})

app.post('/send-message', async (req, res) => {
    try {
        const { to, message } = req.body
        if (!to || !message) {
            return res.status(400).json({ error: 'Missing "to" or "message" fields' })
        }
        if (!sock || !isConnected) {
            return res.status(500).json({ error: 'WhatsApp not connected' })
        }
        const chatId = to.includes('@c.us') || to.includes('@s.whatsapp.net') ? to : `${to}@s.whatsapp.net`
        await sock.sendMessage(chatId, { text: message })
        res.json({ success: true, message: 'Message sent', sentTo: chatId })
    } catch (err) {
        res.status(500).json({ error: err.message })
    }
})

const PORT = process.env.PORT || 3000

app.listen(PORT, () => {
    console.log('='.repeat(50))
    console.log('  WhatsApp AI Bot')
    console.log('='.repeat(50))
    console.log(`Server: http://localhost:${PORT}`)
    console.log(`QR Code: http://localhost:${PORT}/qr.png`)
    console.log(`Status: http://localhost:${PORT}/status`)
    console.log('')
    connectToWhatsApp()
})

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err)
})

process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err)
})
