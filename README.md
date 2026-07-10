# WhatsApp Bot BarberFlow

Bot de suporte via WhatsApp para o sistema BarberFlow.
Funciona 100% gratuito usando Groq IA + Baileys (WhatsApp Web).

## Como Funciona

```
WhatsApp (Baileys) <-> API Python <-> Groq IA (gratuita)
```

1. **Baileys** conecta ao WhatsApp via QR Code (como WhatsApp Web)
2. **API Python** processa as mensagens
3. **Groq IA** gera respostas inteligentes (gratuito)

## Pre-requisitos

- Python 3.10+ (https://www.python.org/downloads/)
- Node.js 18+ (https://nodejs.org)

## Instalacao

### Windows
```bash
# Execute o script de instalacao
instalar_tudo.bat
```

### Manual
```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Instalar dependencias Node.js
cd whatsapp-bridge
npm install
cd ..
```

## Configuracao

1. Crie uma conta gratuita no Groq: https://console.groq.com/keys
2. Crie o arquivo `.env`:
```
GROQ_API_KEY=sua-chave-aqui
```

## Uso

### Iniciar o bot
```bash
python main.py
```

### Escolher opcao
```
1 - Modo teste (interativo)
2 - Iniciar API + WhatsApp Bridge (RECOMENDADO)
3 - Apenas API (para bridge externo)
0 - Sair
```

### Conectar ao WhatsApp
1. Escolha opcao 2
2. Escaneie o QR Code com seu WhatsApp
3. Pronto! O bot esta online

## Comandos do Bot

| Comando | Descricao |
|---------|-----------|
| `/ajuda` | Lista de comandos |
| `/planos` | Ver planos e precos |
| `/horarios` | Horario de suporte |
| `/como_comecar` | Tutorial de uso |
| `/problemas` | Reportar problema |
| `/humano` | Falar com atendente |

### Comandos de Grupo
| Comando | Descricao |
|---------|-----------|
| `/grupo ignorar` | Ignorar mensagens do grupo |
| `/grupo permitir` | Processar mensagens do grupo |
| `/grupo status` | Ver status do grupo |

## Estrutura

```
whatsapp-bot-barbearia/
├── api_server.py           # API Flask
├── bot.py                  # Logica principal
├── ai_handler.py           # Integracao Groq
├── knowledge_base.py       # Base de conhecimento
├── config.py               # Configuracoes
├── main.py                 # Interface principal
├── requirements.txt        # Dependencias Python
├── .env                    # Chave API Groq
└── whatsapp-bridge/
    ├── index.js            # Bridge WhatsApp (Baileys)
    ├── package.json        # Dependencias Node.js
    └── auth_state/         # Credenciais WhatsApp (auto)
```

## Personalizacao

Edite `knowledge_base.py` para:
- Atualizar informacoes do BarberFlow
- Adicionar novos comandos
- Modificar respostas rapidas

## Solucao de Problemas

### QR Code nao aparece
- Verifique se o Node.js esta instalado
- Execute `npm install` na pasta whatsapp-bridge

### Bot nao responde
- Verifique se a API Groq esta funcionando
- Verifique o arquivo `.env` com a chave correta

### WhatsApp desconecta
- As credenciais ficam em whatsapp-bridge/auth_state/
- Delete a pasta e escaneie novamente

## Limitacoes

- Funciona apenas em conversas privadas (DM)
- Grupos precisam ser liberados com `/grupo permitir`
- Maximo 30 mensagens por minuto (limite Groq gratuito)

## Suporte

- WhatsApp: (47) 99675-9164
- Horario: Seg-Sab 9h-19h
