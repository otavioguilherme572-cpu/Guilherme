import tkinter as tk
from tkinter import ttk

# =============================================================================
# GUIA DE ESTILIZAÇÃO DO SISTEMA (CORES, FONTES E TEMA VISUAL)
# =============================================================================
# Dica: Qualquer alteração nas variáveis abaixo atualiza imediatamente toda a 
# interface gráfica do sistema (Login, Painel Principal, Produtos, Usuários, etc.)
# =============================================================================

# -----------------------------------------------------------------------------
# 1. CORES DE FUNDO E ESTRUTURA GERAL DA TELA
# -----------------------------------------------------------------------------
# O que muda: O fundo geral de todas as telas (área cinza claro de fundo da janela)
BG_APP = "#f8fafc"

# O que muda: O fundo dos cartões brancos flutuantes, caixas de formulário e da tabela
BG_CARD = "#ffffff"

# O que muda: A cor alternada nas linhas pares da tabela (efeito 'zebra') e cabeçalhos de colunas
BG_CARD_ALT = "#f1f5f9"


# -----------------------------------------------------------------------------
# 2. TOPO (CABEÇALHO) E MENU LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
# O que muda: A barra escura no topo da janela (onde fica o logo 'SISVENDAS' e o botão 'Sair')
BG_HEADER = "#0f172a"

# O que muda: O fundo do menu vertical à esquerda (onde ficam os botões de navegação)
BG_SIDEBAR = "#1e293b"

# O que muda: A cor do botão do menu lateral quando você passa o mouse por cima
BG_SIDEBAR_HOVER = "#334155"

# O que muda: A cor de destaque do botão da aba atualmente aberta/ativa no menu lateral
BG_SIDEBAR_ACTIVE = "#4f46e5"


# -----------------------------------------------------------------------------
# 3. CORES DOS BOTÕES E AÇÕES PRINCIPAIS (CORES DE DESTAQUE)
# -----------------------------------------------------------------------------
# O que muda: Botão 'Entrar no Sistema', botão 'Buscar', links e item selecionado na tabela
PRIMARY = "#4f46e5"            # Cor normal (Indigo / Azul moderno)
PRIMARY_HOVER = "#4338ca"      # Cor ao passar o mouse por cima
PRIMARY_LIGHT = "#eef2ff"      # Fundo suave do ícone do card de Produtos no Dashboard

# O que muda: Botões de confirmação positiva, como 'Salvar Produto' e 'Cadastrar Usuário'
SUCCESS = "#059669"            # Cor normal (Verde Esmeralda)
SUCCESS_HOVER = "#047857"      # Cor ao passar o mouse por cima
SUCCESS_LIGHT = "#ecfdf5"      # Fundo suave do card de Unidades em Estoque no Dashboard

# O que muda: Botões de alerta/perigo, como 'Excluir Produto', 'Sair' e destaque de estoque zerado
DANGER = "#e11d48"             # Cor normal (Vermelho / Rosa escuro)
DANGER_HOVER = "#be123c"       # Cor ao passar o mouse por cima
DANGER_LIGHT = "#fff1f2"       # Fundo levemente avermelhado nas linhas de produtos com estoque baixo

# O que muda: Cor de avisos e do título ao editar um produto existente ('Editar Produto #...')
WARNING = "#d97706"            # Amarelo / Laranja queimado
WARNING_LIGHT = "#fef3c7"      # Fundo suave de alerta

# O que muda: Cor de indicadores informativos (ex: total de usuários no Dashboard)
INFO = "#0284c7"               # Azul Céu
INFO_LIGHT = "#f0f9ff"         # Fundo suave informativo


# -----------------------------------------------------------------------------
# 4. CORES DE TEXTOS (TIPOGRAFIA)
# -----------------------------------------------------------------------------
# O que muda: Títulos principais de alta prioridade (ex: 'Cadastro de Produtos', 'SISVENDAS')
TEXT_DARK = "#0f172a"          # Preto azulado (quase preto, muito legível)

# O que muda: Textos normais de leitura e valores digitados dentro dos campos de texto
TEXT_BODY = "#334155"          # Cinza escuro (suave para leitura prolongada)

# O que muda: Textos secundários, legendas menores e dicas de preenchimento (ex: 'Acesso Padrão...')
TEXT_MUTED = "#64748b"         # Cinza médio

# O que muda: Texto claro utilizado em cima de fundos escuros (ex: texto dentro dos botões coloridos)
TEXT_LIGHT = "#f8fafc"         # Branco gelo


# -----------------------------------------------------------------------------
# 5. CONTORNOS E LINHAS DIVISÓRIAS (BORDAS)
# -----------------------------------------------------------------------------
# O que muda: A borda cinza ao redor das caixas de digitação (Inputs de texto)
BORDER_COLOR = "#cbd5e1"

# O que muda: As linhas finas de divisão interna dos cartões e divisores horizontais
BORDER_LIGHT = "#e2e8f0"


# -----------------------------------------------------------------------------
# 6. FONTES E TAMANHOS DE LETRA
# -----------------------------------------------------------------------------
# O que muda: A família da fonte em todo o sistema (ex: 'Segoe UI', 'Roboto', 'Arial', 'Inter')
FONT_FAMILY = "Segoe UI"

# Escala de tamanhos:
FONT_TITLE = (FONT_FAMILY, 15, "bold")      # Título principal no topo de cada página
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")   # Subtítulos dos cartões e títulos dos formulários
FONT_SECTION = (FONT_FAMILY, 10, "bold")    # Títulos de pequenas seções internas
FONT_BODY = (FONT_FAMILY, 10)               # Tamanho do texto comum digitado nos campos e tabelas
FONT_BOLD = (FONT_FAMILY, 10, "bold")       # Nomes dos campos (ex: 'Nome do Produto *:', 'Preço:')
FONT_SMALL = (FONT_FAMILY, 9)               # Textos de ajuda, rodapé e dicas
FONT_STAT_NUM = (FONT_FAMILY, 24, "bold")   # Números gigantes dos cartões de métricas do Dashboard


def apply_theme(root: tk.Tk):
    """Configura os estilos visuais globais do ttk com a paleta refinada."""
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Configuração Geral
    style.configure("TFrame", background=BG_APP)
    style.configure("Card.TFrame", background=BG_CARD)
    style.configure("TLabel", background=BG_APP, foreground=TEXT_BODY, font=FONT_BODY)
    style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_BODY, font=FONT_BODY)
    style.configure("Muted.TLabel", background=BG_CARD, foreground=TEXT_MUTED, font=FONT_SMALL)
    style.configure("Title.TLabel", background=BG_CARD, foreground=TEXT_DARK, font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=BG_CARD, foreground=TEXT_DARK, font=FONT_SUBTITLE)

    # Botão Primário (Indigo Moderno)
    style.configure(
        "Primary.TButton",
        background=PRIMARY,
        foreground=TEXT_LIGHT,
        font=FONT_BOLD,
        borderwidth=0,
        focuscolor=PRIMARY_HOVER,
        padding=(14, 8)
    )
    style.map(
        "Primary.TButton",
        background=[("active", PRIMARY_HOVER), ("disabled", "#cbd5e1")],
        foreground=[("disabled", "#94a3b8")]
    )

    # Botão Sucesso (Emerald)
    style.configure(
        "Success.TButton",
        background=SUCCESS,
        foreground=TEXT_LIGHT,
        font=FONT_BOLD,
        borderwidth=0,
        focuscolor=SUCCESS_HOVER,
        padding=(14, 8)
    )
    style.map(
        "Success.TButton",
        background=[("active", SUCCESS_HOVER), ("disabled", "#cbd5e1")],
        foreground=[("disabled", "#94a3b8")]
    )

    # Botão Perigo (Rose)
    style.configure(
        "Danger.TButton",
        background=DANGER,
        foreground=TEXT_LIGHT,
        font=FONT_BOLD,
        borderwidth=0,
        focuscolor=DANGER_HOVER,
        padding=(12, 8)
    )
    style.map(
        "Danger.TButton",
        background=[("active", DANGER_HOVER), ("disabled", "#cbd5e1")],
        foreground=[("disabled", "#94a3b8")]
    )

    # Botão Secundário / Outline
    style.configure(
        "Secondary.TButton",
        background="#e2e8f0",
        foreground=TEXT_BODY,
        font=FONT_BOLD,
        borderwidth=0,
        padding=(12, 8)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#cbd5e1")]
    )

    # Campos de Texto (Entry)
    style.configure(
        "TEntry",
        fieldbackground=BG_CARD,
        foreground=TEXT_DARK,
        bordercolor=BORDER_COLOR,
        lightcolor=PRIMARY,
        darkcolor=BORDER_COLOR,
        padding=6
    )

    # Caixas de Seleção (Combobox)
    style.configure(
        "TCombobox",
        fieldbackground=BG_CARD,
        background=BG_CARD,
        foreground=TEXT_DARK,
        padding=6
    )

    # Tabela de Dados (Treeview)
    style.configure(
        "Treeview",
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=TEXT_BODY,
        rowheight=30,
        font=FONT_BODY,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=BG_CARD_ALT,
        foreground=TEXT_DARK,
        font=(FONT_FAMILY, 9, "bold"),
        padding=(8, 8),
        borderwidth=0
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#e2e8f0")]
    )
    # Fix para compatibilidade com Tkinter 8.6 (Python 3.11):
    # No Tk 8.6, style.map de Treeview pode anular a cor das tags de linha (zebra e alertas).
    try:
        style.map(
            "Treeview",
            foreground=[elm for elm in style.map("Treeview", query_opt="foreground")
                        if elm[:2] != ("!disabled", "!selected")],
            background=[elm for elm in style.map("Treeview", query_opt="background")
                        if elm[:2] != ("!disabled", "!selected")]
        )
    except Exception:
        style.map(
            "Treeview",
            background=[("selected", PRIMARY)],
            foreground=[("selected", TEXT_LIGHT)]
        )

    # Scrollbars
    style.configure("Vertical.TScrollbar", troughcolor=BG_APP, borderwidth=0)
    style.configure("Horizontal.TScrollbar", troughcolor=BG_APP, borderwidth=0)
