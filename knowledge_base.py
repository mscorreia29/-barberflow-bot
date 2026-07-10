# Base de Conhecimento - BarberFlow (v4)
KNOWLEDGE_BASE = {
    "sistema": {
        "nome": "BarberFlow",
        "url_site": "https://barber-flow.store",
        "url_app": "https://barber-flow.store/barberflow",
        "url_cadastro": "https://barber-flow.store/auth?mode=signup",
        "url_login": "https://barber-flow.store/auth",
        "url_manual": "https://barber-flow.store/manual",
        "funcionalidades": [
            "Agendamento online 24h",
            "Painel administrativo",
            "Dashboard com indicadores",
            "Gerenciamento de agenda",
            "Cadastro de clientes e servicos",
            "Comissoes automaticas",
            "Relatorios de faturamento",
            "Notificacoes push",
            "Integracao WhatsApp",
            "Assinaturas recorrentes",
            "Controle de estoque",
            "Avaliacoes de clientes"
        ]
    },
    "planos": {
        "basico": {"nome": "Basico", "preco": "R$ 49,90/mes", "profissionais": "Ate 3"},
        "pro": {"nome": "Pro", "preco": "R$ 89,90/mes", "profissionais": "Ilimitados"},
        "teste": {"nome": "Teste Gratis", "duracao": "7 dias", "plano": "Pro"}
    },
    "suporte": {
        "horario": "Seg-Sab 9h-19h",
        "whatsapp": "(47) 99675-9164"
    }
}

QUICK_RESPONSES = {
    # Saudacao
    "/ola": "Ola! Tudo bem? 😊 Sou do suporte do BarberFlow. Como posso te ajudar?",
    
    # Agradecimento
    "/obrigado": "De nada! Fico feliz em ajudar! 😄 Qualquer outra duvida, e so mandar!",
    
    # Links
    "/teste": "Teste gratis por 7 dias! Acesso completo ao plano Pro.\n\nApos 7 dias, o acesso e bloqueado e voce escolhe um plano:\n- Basico: R$ 49,90/mes\n- Pro: R$ 89,90/mes\n\nSem cartao. Comece agora:\nbarber-flow.store/barberflow",
    
    "/cadastrar": "Crie sua conta gratuitamente:\n\nbarber-flow.store/auth?mode=signup\n\nRapido e facil! Precisa de ajuda?",
    
    "/login": "Pra acessar sua conta:\n\nbarber-flow.store/auth\n\nEsqueceu a senha? La tem opcao de recuperar!",
    
    "/app": "Acesse o BarberFlow aqui:\n\nbarber-flow.store/barberflow\n\nFunciona pelo navegador, sem instalar nada!",
    
    "/site": "Site oficial:\n\nbarber-flow.store\n\nTodas as informacoes la!",
    
    "/manual": "Manual completo:\n\nbarber-flow.store/manual\n\nQualquer duvida, me fala!",
    
    # Compatibilidade
    "/compatibilidade": "Funciona em qualquer dispositivo! 😄\n\n- Celular (Android/iPhone)\n- Tablet\n- Computador\n\nBasta acessar pelo navegador:\nbarber-flow.store/barberflow",
    
    # Planos
    "/planos": "Temos 2 opcoes:\n\n*Basico* - R$ 49,90/mes\nAte 3 profissionais\n\n*Pro* - R$ 89,90/mes\nIlimitado + relatorios + WhatsApp + notificacoes\n\nTeste 7 dias gratis primeiro!",
    
    # Como funciona
    "/como": "Funciona assim:\n\n1. Cria sua conta (gratuita)\n2. Cadastra seus servicos e precos\n3. Adiciona os barbeiros\n4. Configura os horarios\n5. Manda o link pros clientes\n\nEles agendam sozinhos, 24h! 😄",
    
    # Suporte
    "/problemas": "Me conta o que aconteceu:\n\n1. Qual o problema?\n2. Quando comecou?\n3. Consegue mandar um print?\n\nAssim consigo te ajudar melhor!",
    
    "/horarios": "Suporte:\nSeg-Sab das 9h as 19h\nWhatsApp: (47) 99675-9164",
    
    "/humano": "Vou te conectar com um atendente:\n\nWhatsApp: (47) 99675-9164\nHorario: Seg-Sab 9h-19h",
    
    # Recursos
    "/recurso": "O BarberFlow tem tudo:\n\n- Agendamento online 24h\n- Notificacoes automaticas\n- Relatorios de faturamento\n- Comissoes dos barbeiros\n- Assinaturas recorrentes\n- Controle de estoque\n- Avaliacoes de clientes\n\nQuer saber mais?",
    
    "/whatsapp": "Integracao WhatsApp:\n\nEnvia lembretes e confirmacoes automaticamente pros clientes. Plano Pro!",
    
    "/notificacoes": "Notificacoes push:\n\nClientes recebem lembrete 1h antes. Elimina faltas! Plano Pro.",
    
    "/assinaturas": "Assinaturas recorrentes:\n\nCria planos mensais pros clientes. Cobranca via Mercado Pago. Plano Pro.",
    
    # Compartilhar link
    "/compartilhar": "Pra compartilhar com clientes:\n\n1. Acesse barber-flow.store/barberflow\n2. Va em Configuracoes > Link de Agendamento\n3. Copie o link\n4. Envie pros clientes pelo WhatsApp!\n\nEles agendam sozinhos!",
    
    # Cancelar
    "/cancelar": "Para cancelar:\nAcesse Configuracoes > Plano no painel.\n\nSem multa! Mas me conta, algo te desagradou?",
    
    # Sugestoes
    "/sugestao": "Obrigado pela sugestao! Vou registrar no backlog pra equipe avaliar.\n\nSua opiniao e muito importante! 😄",
    
    "/feedback": "Obrigado! Vou registrar no backlog.\n\nSua opiniao ajuda a melhorar o BarberFlow! 😄",
    
    # Barbeiro
    "/barbeiro": "Para vincular um barbeiro:\n1. Acesse barber-flow.store/barberflow\n2. Va em Barbeiros > Novo Barbeiro\n3. Preencha nome e email\n4. Defina uma senha\n5. Salve\n\nO acesso e gerado na hora! Copia e envia pelo WhatsApp pro barbeiro.",
}

SAUDACOES = ["oi", "ola", "bom dia", "boa tarde", "boa noite", "e ai", "fala", "hello", "hi", "hey", "eae"]

PERGUNTAS_COMUNS = {
    "teste gratis": "Teste 7 dias do plano Pro, sem cartao. Acesse barber-flow.store/barberflow e crie sua conta!",
    "como comecar": "Crie sua conta em barber-flow.store/auth?mode=signup, cadastre servicos, barbeiros, e compartilhe o link!",
    "preco": "Basico: R$ 49,90/mes (3 profissionais). Pro: R$ 89,90/mes (ilimitados). Teste 7 dias gratis!",
    "cancelar": "Va em Configuracoes > Plano e cancele. Sem multa!",
    "sincronizar": "Funciona 100% online! Dados sincronizam automaticamente em todos os dispositivos.",
    "app": "Funciona pelo navegador, sem instalar! Acesse barber-flow.store/barberflow",
    "quanto custa": "Basico R$ 49,90/mes. Pro R$ 89,90/mes. Teste 7 dias gratis!",
    "barbeiro": "Barbeiros > Novo Barbeiro no painel. Acesso gerado na hora, copia e manda pelo WhatsApp!",
    "cadastrar barbeiro": "Barbeiros > Novo Barbeiro. Preencha nome, email, senha. Acesso copiado pelo WhatsApp!",
    "agendamento": "Clientes agendam 24h pelo link. Funciona automatico!",
    "comissao": "Calcula comissao dos barbeiros automatico! Plano Pro.",
    "mercado pago": "Assinaturas recorrentes usam Mercado Pago. Plano Pro.",
    "relatorio": "Dashboard com faturamento, comissoes, agendamentos. Plano Pro.",
    "estoque": "Controle de estoque disponivel nos dois planos!",
    "avaliacao": "Clientes podem avaliar o servico no app. Disponivel nos dois planos!",
    "compartilhar link": "Configuracoes > Link de Agendamento. Copie e envie pros clientes!"
}
