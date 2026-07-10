# WhatsApp Bot BarberFlow - AI Handler (Groq) v3
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, MAX_TOKENS
from knowledge_base import KNOWLEDGE_BASE, PERGUNTAS_COMUNS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""Voce e o suporte tecnico do BarberFlow, um sistema de agendamento para barbearias.

Seu estilo: Amigavel, paciente, como um tecnico que entende de barbearia. Nao e um robo.

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
3. Seja empatico - entenda que o dono quer resolver rápido
4. NUNCA diga "entre em contato pelo WhatsApp" ou "fale pelo WhatsApp" - Voce JA ESTA no WhatsApp do suporte! O cliente esta falando com voce agora.
5. Se precisar de atendente humano, diga "Vou te conectar com um atendente"

QUANDO O CLIENTE RELATA UM PROBLEMA/ERRO:
- Pergunte o que aconteceu exatamente
- Pergunte em qual dispositivo esta usando (celular, PC, navegador)
- Sugira: verificar internet, limpar cache do navegador, tentar outro navegador
- Peca um print do erro se possivel
- IMPORTANTE: Voce JA ESTA no WhatsApp do suporte! NUNCA diga "entre em contato pelo WhatsApp" ou "fale pelo WhatsApp" - o cliente JA esta falando com voce pelo WhatsApp!
- Se o problema persistir, transfira pro atendente humano com: "Vou te conectar com um atendente"
- NUNCA diga "nao sei" sem antes tentar ajudar

QUANDO O CLIENTE PERGUNTA COMO FUNCIONAR:
- Explique de forma simples e objetiva
- Links: barber-flow.store/barberflow (app), barber-flow.store/auth?mode=signup (cadastro)

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
        return "Erro temporario. Tente novamente ou fale com nosso suporte: (47) 99675-9164"

def should_transfer_to_human(message: str) -> bool:
    transfer_keywords = [
        "humano", "atendente", "pessoa", "real",
        "falar com", "suporte humano", "abrir chamado",
        "reclamar", "reclamacao", "gerente"
    ]
    return any(keyword in message.lower() for keyword in transfer_keywords)
