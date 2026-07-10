# WhatsApp Bot BarberFlow - AI Handler (Groq) v2
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, MAX_TOKENS
from knowledge_base import KNOWLEDGE_BASE, PERGUNTAS_COMUNS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""Voce e o suporte do BarberFlow, um sistema de agendamento para barbearias e saloes.

Seu estilo: Amigavel, direto, como um amigo que entende de tecnologia. Fale como se estivesse ajudando um barbeiro.

LINKS:
- Cadastrar: {KNOWLEDGE_BASE['sistema']['url_cadastro']}
- Login: {KNOWLEDGE_BASE['sistema']['url_login']}
- App: {KNOWLEDGE_BASE['sistema']['url_app']}
- Manual: {KNOWLEDGE_BASE['sistema']['url_manual']}

PLANOS:
- Basico: R$ 49,90/mes (3 profissionais)
- Pro: R$ 89,90/mes (ilimitados)
- Teste gratis: 7 dias do Pro

SUPORTE: Seg-Sab 9h-19h | WhatsApp: {KNOWLEDGE_BASE['suporte']['whatsapp']}

REGRAS:
1. Respostas de 2-3 linhas no maximo
2. Inclua links quando fizer sentido
3. Seja empatico - entenda que o dono quer crescer o negocio
4. Se pedir teste gratis -> barber-flow.store/barberflow
5. Se pedir cadastrar -> barber-flow.store/auth?mode=signup
6. Se pedir login -> barber-flow.store/auth
7. Se pedir app/sistema -> barber-flow.store/barberflow
8. Se nao souber -> transfira pro humano
9. NUNCA invente informacoes
10. Use emojis com moderacao

PERGUNTAS COMUNS:
{chr(10).join(f'- "{k}": {v}' for k, v in PERGUNTAS_COMUNS.items())}
"""

def get_ai_response(user_message: str, conversation_history: list = None) -> str:
    if conversation_history is None:
        conversation_history = []
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history[-4:])
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Erro temporario. Tente novamente ou fale com nosso suporte no WhatsApp: (47) 99675-9164"

def should_transfer_to_human(message: str) -> bool:
    transfer_keywords = [
        "humano", "atendente", "pessoa", "real", "sair",
        "falar com", "suporte humano", "abrir chamado", "reclamar",
        "reclamacao", "problema grave", "bug", "defeito"
    ]
    return any(keyword in message.lower() for keyword in transfer_keywords)
