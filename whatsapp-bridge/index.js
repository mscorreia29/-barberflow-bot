const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

// URL da API no Railway (ALTERE PARA SEU LINK)
const BOT_API_URL = process.env.BOT_API_URL || 'http://127.0.0.1:5000';
const AUTH_DIR = path.join(__dirname, 'auth_state');
const GROUPS_FILE = path.join(__dirname, 'groups.json');

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

function isGroupCommand(text) {
    return text.toLowerCase().startsWith('/grupo');
}

function handleGroupCommand(text, groupName) {
    const cmd = text.toLowerCase().trim();
    
    if (cmd === '/grupo ignorar') {
        if (!ignoredGroups.includes(groupName)) {
            ignoredGroups.push(groupName);
            saveIgnoredGroups();
            return `Grupo "${groupName}" ignorado.`;
        }
        return `Grupo ja ignorado.`;
    }
    
    if (cmd === '/grupo permitir') {
        const idx = ignoredGroups.indexOf(groupName);
        if (idx !== -1) {
            ignoredGroups.splice(idx, 1);
            saveIgnoredGroups();
            return `Grupo "${groupName}" ativado.`;
        }
        return `Grupo ja ativo.`;
    }
    
    if (cmd === '/grupo status') {
        const status = ignoredGroups.includes(groupName) ? 'IGNORADO' : 'ATIVO';
        return `Status: ${status}`;
    }
    
    return `Comandos:\n/grupo ignorar\n/grupo permitir\n/grupo status`;
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
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('\n===========================================');
            console.log('  ESCANEIE O QR CODE COM SEU WHATSAPP');
            console.log('===========================================\n');
            qrcode.generate(qr, { small: true });
            console.log('\nApos escanear, aguarde a conexao...\n');
        }
        
        if (connection === 'close') {
            const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
            
            if (statusCode === DisconnectReason.loggedOut) {
                console.log('Desconectado. Limpe auth_state e reinicie.');
                process.exit(1);
            } else {
                console.log('Desconectado. Reconectando...');
                connectToWhatsApp();
            }
        }
        
        if (connection === 'open') {
            console.log('===========================================');
            console.log('  BOT CONECTADO COM SUCESSO!');
            console.log(`  API: ${BOT_API_URL}`);
            console.log('  Aguardando mensagens...');
            console.log('===========================================\n');
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
                
                if (isGroupCommand(text)) {
                    const response = handleGroupCommand(text, groupName);
                    await sock.sendMessage(chatJid, { text: response });
                    continue;
                }
                
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

// Verificar API
console.log('===========================================');
console.log('  BARBERFLOW WHATSAPP BOT');
console.log('===========================================\n');
console.log(`Conectando a API: ${BOT_API_URL}\n`);

fetch(`${BOT_API_URL}/health`)
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            console.log('API detectada! Iniciando WhatsApp...\n');
            connectToWhatsApp();
        } else {
            console.error('API retornou resposta invalida.');
            process.exit(1);
        }
    })
    .catch(err => {
        console.error(`ERRO: API nao esta rodando em ${BOT_API_URL}`);
        console.error(`Erro: ${err.message}`);
        console.error('\nVerifique se a API esta rodando no Railway.');
        process.exit(1);
    });
