# AutoAssist Bot - Configuracao
import os
from dotenv import load_dotenv

load_dotenv()

# Groq (gratuito)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Bot Settings
BOT_NAME = "AutoAssist"
BOT_PHONE = os.getenv("BOT_PHONE", "")

# Support Hours
SUPPORT_HOURS = "Seg-Sex: 8h as 18h | Sab: 8h as 14h"

# AI Settings
AI_MODEL = "llama-3.3-70b-versatile"  # Gratuito no Groq
MAX_TOKENS = 200

# Ignorar grupos (só responder DMs)
IGNORE_GROUPS = True
