# WhatsApp Bot BarberFlow - AI Handler (Groq)
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, MAX_TOKENS
from knowledge_base import KNOWLEDGE_BASE, PERGUNTAS_COMUNS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""Voce e o suporte do BarberFlow. Seja MUITO breve e direto.

LINKS IMPORTANTES:
- Site: {KNOWLEDGE_BASE['sistema']['url_site']}
- App: {KNOWLEDGE_BASE['sistema']['url_app']}
- Cadastro: {KNOWLEDGE_BASE['sistema']['url_cadastro']}
- Login: {KNOWLEDGE_BASE['sistema']['url_login']}
- Manual: {KNOWLEDGE_BASE['sistema']['url_manual']}

PLANOS:
- Basico: R$ 49,90/mes (3 profissionais)
- Pro: R$ 89,90/mes (ilimitados)
- Teste gratis: 7 dias do Pro

SUPORTE: Seg-Sab 9h-19h | WhatsApp: {KNOWLEDGE_BASE['suporte']['whatsapp']}

REGRAS OBRIGATORIAS:
1. Respostas de MAXIMO 2-3 linhas
2. SEMPRE inclua links quando relevante
3. Se pedir teste gratis -> envie barber-flow.store/barberflow
4. Se pedir cadastrar -> envie barber-flow.store/auth?mode=signup
5. Se pedir login -> envie barber-flow.store/auth
6. Se pedir app/sistema -> envie barber-flow.store/barberflow
7. Se nao souber -> digite /humano
8. NUNCA invente informacoes
9. Seja amigavel mas direto

PERGUNTAS COMUNS E RESPOSTAS:
{chr(10).join(f'- "{k}": {v[:100]}...' if len(v) > 100 else f'- "{k}": {v}' for k, v in PERGUNTAS_COMUNS.items())}
"""

def get_ai_response(user_message: str, conversation_history: list = None) -> str:
    """Obtem resposta da IA baseada na mensagem do usuario"""
    
    if conversation_history is None:
        conversation_history = []
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history[-4:])  # Ultimas 4 mensagens apenas
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.5  # Menos criativo, mais preciso
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Erro temporario. Tente novamente ou digite /humano."

def should_transfer_to_human(message: str) -> bool:
    """Verifica se a mensagem indica que o cliente quer falar com humano"""
    transfer_keywords = [
        "humano", "atendente", "pessoa", "real", "sair",
        "falar com", "suporte humano", "abrir chamado"
    ]
    return any(keyword in message.lower() for keyword in transfer_keywords)
