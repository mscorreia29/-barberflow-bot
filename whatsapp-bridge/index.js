const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

// Configuracoes
const BOT_API_URL = 'http://127.0.0.1:5000';
const AUTH_DIR = path.join(__dirname, 'auth_state');
const GROUPS_FILE = path.join(__dirname, 'groups.json');

// Logger silencioso (so erros)
const logger = pino({ level: 'silent' });

// Carregar grupos ignorados
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

// Verificar se mensagem e comando de grupo
function isGroupCommand(text) {
    return text.toLowerCase().startsWith('/grupo');
}

// Comandos de gerenciamento de grupo
function handleGroupCommand(text, groupName) {
    const cmd = text.toLowerCase().trim();
    
    if (cmd === '/grupo ignorar') {
        if (!ignoredGroups.includes(groupName)) {
            ignoredGroups.push(groupName);
            saveIgnoredGroups();
            return `Grupo "${groupName}" adicionado a lista de ignorados. Mensagens deste grupo nao serao processadas.`;
        }
        return `Grupo "${groupName}" ja esta na lista de ignorados.`;
    }
    
    if (cmd === '/grupo permitir') {
        const idx = ignoredGroups.indexOf(groupName);
        if (idx !== -1) {
            ignoredGroups.splice(idx, 1);
            saveIgnoredGroups();
            return `Grupo "${groupName}" removido da lista de ignorados. Mensagens deste grupo serao processadas.`;
        }
        return `Grupo "${groupName}" nao esta na lista de ignorados.`;
    }
    
    if (cmd === '/grupo status') {
        const status = ignoredGroups.includes(groupName) ? 'IGNORADO' : 'ATIVO';
        return `Status do grupo "${groupName}": ${status}`;
    }
    
    return `Comandos de grupo disponiveis:\n/grupo ignorar - Ignorar mensagens deste grupo\n/grupo permitir - Processar mensagens deste grupo\n/grupo status - Ver status atual`;
}

// Enviar mensagem para o bot Python e obter resposta
async function getBotResponse(phone, message, isGroup = false) {
    try {
        const response = await fetch(`${BOT_API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: phone,
                message: message,
                is_group: isGroup
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Erro ao comunicar com bot:', error.message);
        return null;
    }
}

// Conectar ao WhatsApp
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
    
    // QR Code
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
                console.log('Desconectado. Limpe a pasta auth_state e reinicie.');
                process.exit(1);
            } else {
                console.log('Desconectado. Reconectando...');
                connectToWhatsApp();
            }
        }
        
        if (connection === 'open') {
            console.log('===========================================');
            console.log('  BOT CONECTADO COM SUCESSO!');
            console.log('  Aguardando mensagens...');
            console.log('  Pressione Ctrl+C para sair');
            console.log('===========================================\n');
        }
    });
    
    // Salvar credenciais
    sock.ev.on('creds.update', saveCreds);
    
    // Receber mensagens
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;
        
        for (const msg of messages) {
            // Ignorar mensagens proprias
            if (msg.key.fromMe) continue;
            
            // Ignorar mensagens de status
            if (msg.key.remoteJid === 'status@broadcast') continue;
            
            const isGroup = msg.key.remoteJid.endsWith('@g.us');
            const senderJid = isGroup ? msg.key.participant : msg.key.remoteJid;
            const chatJid = msg.key.remoteJid;
            
            // Obter texto da mensagem
            let text = '';
            if (msg.message?.conversation) {
                text = msg.message.conversation;
            } else if (msg.message?.extendedTextMessage?.text) {
                text = msg.message.extendedTextMessage.text;
            } else if (msg.message?.imageMessage?.caption) {
                text = msg.message.imageMessage.caption;
            } else {
                continue; // Ignorar mensagens sem texto
            }
            
            if (!text.trim()) continue;
            
            // Extrair nome do grupo se for grupo
            let groupName = '';
            if (isGroup) {
                const groupMeta = await sock.groupMetadata(chatJid);
                groupName = groupMeta.subject;
                
                // Verificar comandos de grupo
                if (isGroupCommand(text)) {
                    const response = handleGroupCommand(text, groupName);
                    await sock.sendMessage(chatJid, { text: response });
                    continue;
                }
                
                // Ignorar grupo se estiver na lista
                if (ignoredGroups.includes(groupName)) {
                    continue;
                }
            }
            
            // Formatar numero do telefone
            const phone = senderJid.replace(/@s\.whatsapp\.net$/, '').replace(/@.*$/, '');
            
            console.log(`[${isGroup ? 'GRUPO:' + groupName : 'DM'}] ${phone}: ${text.substring(0, 50)}...`);
            
            // Obter resposta do bot
            const response = await getBotResponse(phone, text, isGroup);
            
            if (response) {
                // Enviar resposta
                if (isGroup) {
                    // Em grupo, responder mencionando o usuario
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
console.log('  Bridge de conexao');
console.log('===========================================\n');
console.log('Verificando se o bot Python esta rodando...\n');

// Verificar se bot Python esta rodando
fetch(`${BOT_API_URL}/health`)
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            console.log('Bot Python detectado! Iniciando conexao WhatsApp...\n');
            connectToWhatsApp();
        } else {
            console.error('Bot Python retornou resposta invalida.');
            process.exit(1);
        }
    })
    .catch(err => {
        console.error('ERRO: Bot Python nao esta rodando!');
        console.error('Execute primeiro: python main.py');
        console.error(`Erro: ${err.message}`);
        process.exit(1);
    });
