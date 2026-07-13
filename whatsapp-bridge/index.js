process.on('uncaughtException', (err) => {
    console.error('[FATAL] uncaughtException:', err.message);
    console.error(err.stack);
});

process.on('unhandledRejection', (reason) => {
    console.error('[FATAL] unhandledRejection:', reason);
});

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
const QR_FILE = path.join(__dirname, 'qrcode.png');

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
        console.error('[Bridge] Erro ao comunicar com bot:', error.message);
        return null;
    }
}

async function connectToWhatsApp() {
    try {
        console.log('[Bridge] Iniciando conexao WhatsApp...');
        console.log(`[Bridge] API URL: ${BOT_API_URL}`);

        const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
        const { version } = await fetchLatestBaileysVersion();
        console.log(`[Bridge] Baileys version: ${JSON.stringify(version)}`);

        const sock = makeWASocket({
            version,
            auth: state,
            logger,
            printQRInTerminal: false,
            browser: ['AutoAssist', 'Chrome', '1.0.0'],
            markOnlineOnConnect: true
        });

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            console.log(`[Bridge] Connection: ${connection || 'none'}, qr: ${qr ? 'YES' : 'no'}`);

            if (qr) {
                console.log('[Bridge] QR CODE RECEBIDO!');
                try {
                    const qrBuffer = await toBuffer(qr);
                    fs.writeFileSync(QR_FILE, qrBuffer);
                    console.log(`[Bridge] QR salvo: ${qrBuffer.length} bytes`);
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
                }
                setTimeout(connectToWhatsApp, 5000);
            }

            if (connection === 'open') {
                console.log('[Bridge] CONECTADO!');
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
                else if (msg.message?.buttonsResponseMessage?.selectedButtonId) text = msg.message.buttonsResponseMessage.selectedButtonId;
                else if (msg.message?.listResponseMessage?.singleSelectReply?.selectedRowId) text = msg.message.listResponseMessage.singleSelectReply.selectedRowId;
                else continue;

                if (!text.trim()) continue;

                if (isGroup) {
                    try {
                        const groupMeta = await sock.groupMetadata(chatJid);
                        if (ignoredGroups.includes(groupMeta.subject)) continue;
                    } catch (e) {}
                }

                const phone = senderJid.replace(/@s\.whatsapp\.net$/, '').replace(/@.*$/, '');
                console.log(`[Bridge] [${isGroup ? 'GRUPO' : 'DM'}] ${phone}: ${text.substring(0, 80)}`);

                const response = await getBotResponse(phone, text, isGroup);

                if (response) {
                    try {
                        if (isGroup) {
                            await sock.sendMessage(chatJid, { text: `@${phone.split('@')[0]} ${response}`, mentions: [senderJid] });
                        } else {
                            await sock.sendMessage(chatJid, { text: response });
                        }
                        console.log(`[Bridge] Resposta enviada para ${phone}`);
                    } catch (e) {
                        console.error(`[Bridge] Erro ao enviar para ${phone}:`, e.message);
                    }
                }
            }
        });

        console.log('[Bridge] Socket criado, aguardando conexao...');
    } catch (error) {
        console.error('[Bridge] ERRO FATAL:', error.message);
        console.error(error.stack);
        setTimeout(connectToWhatsApp, 10000);
    }
}

console.log('[Bridge] ===========================================');
console.log('[Bridge] AUTOASSIST WHATSAPP BOT');
console.log(`[Bridge] API: ${BOT_API_URL}`);
console.log('[Bridge] ===========================================');
connectToWhatsApp();
