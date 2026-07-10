const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const pino = require('pino');
const { toBuffer } = require('qrcode');
const fs = require('fs');
const path = require('path');

const API_PORT = process.env.PORT || 5000;
const BOT_API_URL = `http://127.0.0.1:${API_PORT}`;
const AUTH_DIR = path.join(__dirname, 'auth_state');
const GROUPS_FILE = path.join(__dirname, 'groups.json');
const QR_FILE = '/app/whatsapp_bridge_qr.png';

const logger = pino({ level: 'silent' });

let ignoredGroups = [];
if (fs.existsSync(GROUPS_FILE)) {
    try { ignoredGroups = JSON.parse(fs.readFileSync(GROUPS_FILE, 'utf8')); } catch (e) { ignoredGroups = []; }
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
    try {
        console.log('[Bridge] Iniciando conexao WhatsApp...');
        console.log(`[Bridge] API URL: ${BOT_API_URL}`);
        
        const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
        const { version } = await fetchLatestBaileysVersion();
        console.log(`[Bridge] Baileys version: ${version}`);
        
        const sock = makeWASocket({
            version,
            auth: state,
            logger,
            printQRInTerminal: true,
            browser: ['BarberFlow Bot', 'Chrome', '1.0.0']
        });
        
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                console.log('[Bridge] QR CODE RECEBIDO! Salvando...');
                try {
                    const qrBuffer = await toBuffer(qr);
                    fs.writeFileSync(QR_FILE, qrBuffer);
                    console.log(`[Bridge] QR salvo em: ${QR_FILE}`);
                    
                    const qrLocal = path.join(__dirname, 'qrcode.png');
                    fs.writeFileSync(qrLocal, qrBuffer);
                    console.log(`[Bridge] QR tambem salvo em: ${qrLocal}`);
                } catch (e) {
                    console.error('[Bridge] Erro ao salvar QR:', e.message);
                }
            }
            
            if (connection === 'close') {
                const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
                console.log(`[Bridge] Desconectado. Status: ${statusCode}`);
                
                if (statusCode === DisconnectReason.loggedOut) {
                    console.log('[Bridge] Sessao invalida. Limpando...');
                    if (fs.existsSync(AUTH_DIR)) fs.rmSync(AUTH_DIR, { recursive: true });
                    setTimeout(connectToWhatsApp, 3000);
                } else {
                    console.log('[Bridge] Reconectando em 5s...');
                    setTimeout(connectToWhatsApp, 5000);
                }
            }
            
            if (connection === 'open') {
                console.log('[Bridge] CONECTADO AO WHATSAPP!');
                if (fs.existsSync(QR_FILE)) fs.unlinkSync(QR_FILE);
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
                if (msg.message?.conversation) text = msg.message.conversation;
                else if (msg.message?.extendedTextMessage?.text) text = msg.message.extendedTextMessage.text;
                else if (msg.message?.imageMessage?.caption) text = msg.message.imageMessage.caption;
                else continue;
                
                if (!text.trim()) continue;
                
                if (isGroup) {
                    const groupMeta = await sock.groupMetadata(chatJid);
                    const groupName = groupMeta.subject;
                    if (ignoredGroups.includes(groupName)) continue;
                }
                
                const phone = senderJid.replace(/@s\.whatsapp\.net$/, '').replace(/@.*$/, '');
                console.log(`[Bridge] [${isGroup ? 'GRUPO' : 'DM'}] ${phone}: ${text.substring(0, 50)}`);
                
                const response = await getBotResponse(phone, text, isGroup);
                
                if (response) {
                    if (isGroup) {
                        await sock.sendMessage(chatJid, { text: `@${phone.split('@')[0]} ${response}`, mentions: [senderJid] });
                    } else {
                        await sock.sendMessage(chatJid, { text: response });
                    }
                    console.log(`[Bridge] Resposta enviada para ${phone}`);
                }
            }
        });
    } catch (error) {
        console.error('[Bridge] ERRO FATAL:', error.message);
        console.error(error.stack);
        setTimeout(connectToWhatsApp, 10000);
    }
}

console.log('[Bridge] ===========================================');
console.log('[Bridge] BARBERFLOW WHATSAPP BOT');
console.log('[Bridge] ===========================================');
connectToWhatsApp();
