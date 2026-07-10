const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const pino = require('pino');
const { toBuffer } = require('qrcode');
const fs = require('fs');
const path = require('path');

// API interna do Railway
const BOT_API_URL = process.env.BOT_API_URL || 'http://127.0.0.1:5000';
const AUTH_DIR = path.join(__dirname, 'auth_state');
const GROUPS_FILE = path.join(__dirname, 'groups.json');
const QR_FILE = path.join(__dirname, 'qrcode.png');

const logger = pino({ level: 'silent' });

let ignoredGroups = [];
if (fs.existsSync(GROUPS_FILE)) {
    try {
        ignoredGroups = JSON.parse(fs.readFileSync(GROUPS_FILE, 'utf8'));
    } catch (e) {
        ignoredGroups = [];
    }
}

function saveIgnoredGroups() {
    fs.writeFileSync(GROUPS_FILE, JSON.stringify(ignoredGroups, null, 2));
}

async function getBotResponse(phone, message, isGroup = false) {
    try {
        const response = await fetch(`${BOT_API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, message, is_group: isGroup })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Erro ao comunicar com bot:', error.message);
        return null;
    }
}

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion();
    
    const sock = makeWASocket({
        version,
        auth: state,
        logger,
        printQRInTerminal: false,
        browser: ['BarberFlow Bot', 'Chrome', '1.0.0']
    });
    
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('\n===========================================');
            console.log('  QR CODE GERADO!');
            console.log('===========================================');
            console.log('Acesse http://localhost:5000/qr para escanear');
            console.log('Ou veja o QR no terminal abaixo:\n');
            
            // Salvar QR como imagem
            const qrBuffer = await toBuffer(qr);
            fs.writeFileSync(QR_FILE, qrBuffer);
            console.log('QR salvo em: whatsapp-bridge/qrcode.png\n');
            
            // Gerar QR no terminal (fallback)
            const qrcode = require('qrcode-terminal');
            qrcode.generate(qr, { small: true });
        }
        
        if (connection === 'close') {
            const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
            
            if (statusCode === DisconnectReason.loggedOut) {
                console.log('Desconectado. Sessao invalida.');
                // Limpar auth para gerar novo QR
                if (fs.existsSync(AUTH_DIR)) {
                    fs.rmSync(AUTH_DIR, { recursive: true });
                }
                connectToWhatsApp();
            } else {
                console.log('Desconectado. Reconectando...');
                connectToWhatsApp();
            }
        }
        
        if (connection === 'open') {
            console.log('===========================================');
            console.log('  BOT WHATSAPP CONECTADO!');
            console.log('===========================================');
            // Remover QR antigo
            if (fs.existsSync(QR_FILE)) {
                fs.unlinkSync(QR_FILE);
            }
        }
    });
    
    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;
        
        for (const msg of messages) {
            if (msg.key.fromMe) continue;
            if (msg.key.remoteJid === 'status@broadcast') continue;
            
            const isGroup = msg.key.remoteJid.endsWith('@g.us');
            const senderJid = isGroup ? msg.key.participant : msg.key.remoteJid;
            const chatJid = msg.key.remoteJid;
            
            let text = '';
            if (msg.message?.conversation) {
                text = msg.message.conversation;
            } else if (msg.message?.extendedTextMessage?.text) {
                text = msg.message.extendedTextMessage.text;
            } else if (msg.message?.imageMessage?.caption) {
                text = msg.message.imageMessage.caption;
            } else {
                continue;
            }
            
            if (!text.trim()) continue;
            
            let groupName = '';
            if (isGroup) {
                const groupMeta = await sock.groupMetadata(chatJid);
                groupName = groupMeta.subject;
                if (ignoredGroups.includes(groupName)) continue;
            }
            
            const phone = senderJid.replace(/@s\.whatsapp\.net$/, '').replace(/@.*$/, '');
            
            console.log(`[${isGroup ? 'GRUPO:' + groupName : 'DM'}] ${phone}: ${text.substring(0, 50)}...`);
            
            const response = await getBotResponse(phone, text, isGroup);
            
            if (response) {
                if (isGroup) {
                    await sock.sendMessage(chatJid, {
                        text: `@${phone.split('@')[0]} ${response}`,
                        mentions: [senderJid]
                    });
                } else {
                    await sock.sendMessage(chatJid, { text: response });
                }
                console.log(`Resposta enviada para ${phone}`);
            }
        }
    });
}

// Iniciar
console.log('===========================================');
console.log('  BARBERFLOW WHATSAPP BOT');
console.log('===========================================\n');

connectToWhatsApp();
