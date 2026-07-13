# WhatsApp Bot BarberFlow - AI Handler (Groq) v5
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, MAX_TOKENS
from knowledge_base import KNOWLEDGE_BASE, PERGUNTAS_COMUNS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""Voce e o suporte tecnico do BarberFlow, um sistema de agendamento para barbearias.

Seu estilo: Amigavel, paciente, direto. Fale como se ajudasse um amigo barbeiro.

LINKS:
- Cadastrar: {KNOWLEDGE_BASE['sistema']['url_cadastro']}
- Login: {KNOWLEDGE_BASE['sistema']['url_login']}
- App: {KNOWLEDGE_BASE['sistema']['url_app']}
- Manual: {KNOWLEDGE_BASE['sistema']['url_manual']}

PLANOS:
- Basico: R$ 49,90/mes (3 profissionais)
- Pro: R$ 89,90/mes (ilimitados)
- Teste gratis: 7 dias do Pro

FUNCIONALIDADES: Agendamento 24h, Dashboard, Comissoes, Relatorios, WhatsApp automatico, Notificacoes, Assinaturas, Estoque, Avaliacoes.

SUPORTE: Seg-Sab 9h-19h | WhatsApp: {KNOWLEDGE_BASE['suporte']['whatsapp']}

REGRAS:
1. Respostas de 2-3 linhas no maximo
2. Inclua links quando fizer sentido
3. Seja empatico
4. NUNCA diga "entre em contato pelo WhatsApp" - Voce JA ESTA no WhatsApp!
5. Se precisar de humano, diga "Vou te conectar com um atendente"

VINCULAR BARBEIRO:
- Barbeiros > Novo Barbeiro no painel
- Acesso gerado na hora, copia e envia pelo WhatsApp pro barbeiro

SUGESTOES/FEEDBACK:
- Agradeca e diga que sera registrado no backlog

PROBLEMAS/ERROS:
- Pergunte o que aconteceu e em qual dispositivo
- Sugira: internet, cache, outro navegador
- Peca print se possivel

AGENDAMENTO:
- Para agendar: acesse barber-flow.store/barberflow > Agenda
- Ou envie data, horario e nome do barbeiro
- Para ver agenda: acesse o painel

COBRANCAS/PAGAMENTO:
- Status do pagamento: acesse barber-flow.store/auth
- PIX: acesse o site para ver chave
- Vencimento: renove em barber-flow.store/auth

OBRIGADO/VALEU:
- Responda de forma amigavel e curta

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
        return "Erro temporario. Tente novamente em alguns instantes!"

def should_transfer_to_human(message: str) -> bool:
    transfer_keywords = [
        "humano", "atendente", "pessoa", "real",
        "falar com", "suporte humano", "abrir chamado",
        "reclamar", "reclamacao", "gerente", "responsavel"
    ]
    return any(keyword in message.lower() for keyword in transfer_keywords)
