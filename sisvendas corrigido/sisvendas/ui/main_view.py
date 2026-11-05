import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict

from modules.auth import Session
from ui.theme import (
    BG_APP, BG_CARD, BG_HEADER, BG_SIDEBAR, BG_SIDEBAR_HOVER, BG_SIDEBAR_ACTIVE,
    PRIMARY, PRIMARY_HOVER, DANGER, DANGER_HOVER, TEXT_DARK, TEXT_BODY,
    TEXT_MUTED, TEXT_LIGHT, BORDER_LIGHT, FONT_TITLE, FONT_SUBTITLE,
    FONT_SECTION, FONT_BODY, FONT_BOLD, FONT_SMALL
)
from ui.views.dashboard_view import DashboardView
from ui.views.produtos_view import ProdutosView
from ui.views.usuarios_view import UsuariosView
from ui.views.vendas_view import VendasView


class MainView(tk.Frame):
    """
    Interface Gráfica do Painel Principal com paleta profissional.
    Estrutura com Cabeçalho Superior em Deep Navy, Barra Lateral (Sidebar) em Slate
    e Área Central em Slate 50.
    """
    def __init__(self, parent: tk.Widget, on_logout: Callable[[], None]):
        super().__init__(parent, bg=BG_APP)
        self.on_logout = on_logout
        self.aba_atual = None
        self.botoes_sidebar: Dict[str, tk.Button] = {}
        self.views: Dict[str, tk.Widget] = {}

        self._criar_layout()
        self.mostrar_aba("dashboard")

    def _criar_layout(self):
        # ---------------------------------------------------------------------
        # 1. BARRA SUPERIOR (HEADER)
        # ---------------------------------------------------------------------
        self.header = tk.Frame(self, bg=BG_HEADER, height=58, padx=22)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        # Logotipo / Nome do Sistema
        lbl_logo = tk.Label(
            self.header,
            text="🛒 SISVENDAS",
            bg=BG_HEADER,
            fg="#818cf8",  # Indigo 400
            font=("Segoe UI", 14, "bold")
        )
        lbl_logo.pack(side="left")

        lbl_slogan = tk.Label(
            self.header,
            text="| Gestão Comercial & PDV",
            bg=BG_HEADER,
            fg="#94a3b8",  # Slate 400
            font=FONT_SMALL
        )
        lbl_slogan.pack(side="left", padx=(8, 0))

        # Painel do Usuário Logado & Botão Sair (à direita)
        user_panel = tk.Frame(self.header, bg=BG_HEADER)
        user_panel.pack(side="right")

        # Pill do usuário
        pill_user = tk.Frame(user_panel, bg="#1e293b", padx=12, pady=4)
        pill_user.pack(side="left", padx=(0, 12))

        user_info_txt = f"👤 {Session.nome or Session.usuario}  •  {Session.cargo}"
        lbl_user = tk.Label(
            pill_user,
            text=user_info_txt,
            bg="#1e293b",
            fg="#f8fafc",
            font=FONT_SMALL
        )
        lbl_user.pack()

        # Botão Logout em Rose
        btn_sair = tk.Button(
            user_panel,
            text="🚪 Sair",
            bg=DANGER,
            fg=TEXT_LIGHT,
            activebackground=DANGER_HOVER,
            activeforeground=TEXT_LIGHT,
            font=FONT_SMALL,
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._confirmar_logout
        )
        btn_sair.pack(side="right")

        # ---------------------------------------------------------------------
        # 2. CORPO (SIDEBAR + CONTEÚDO)
        # ---------------------------------------------------------------------
        body_frame = tk.Frame(self, bg=BG_APP)
        body_frame.pack(side="bottom", fill="both", expand=True)

        # Barra Lateral (Sidebar)
        self.sidebar = tk.Frame(body_frame, bg=BG_SIDEBAR, width=225, padx=12, pady=18)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        lbl_menu_tit = tk.Label(
            self.sidebar,
            text="NAVEGAÇÃO",
            bg=BG_SIDEBAR,
            fg="#64748b",
            font=("Segoe UI", 8, "bold")
        )
        lbl_menu_tit.pack(anchor="w", padx=10, pady=(0, 12))

        # Botões de Navegação da Sidebar
        self._adicionar_botao_sidebar("dashboard", "📊  Início / Painel", lambda: self.mostrar_aba("dashboard"))
        self._adicionar_botao_sidebar("produtos", "📦  Produtos & Estoque", lambda: self.mostrar_aba("produtos"))
        self._adicionar_botao_sidebar("vendas", "🛒  Frente de Caixa (PDV)", lambda: self.mostrar_aba("vendas"))

        if Session.is_admin():
            self._adicionar_botao_sidebar("usuarios", "👥  Usuários & Acesso", lambda: self.mostrar_aba("usuarios"))

        # Rodapé da Sidebar
        sidebar_footer = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        sidebar_footer.pack(side="bottom", fill="x", pady=(0, 5))

        lbl_versao = tk.Label(
            sidebar_footer,
            text="SisVendas v1.0 • Offline SQLite\nAmbiente Seguro",
            bg=BG_SIDEBAR,
            fg="#64748b",
            font=("Segoe UI", 7),
            justify="center"
        )
        lbl_versao.pack(fill="x")

        # Área de Conteúdo Dinâmico
        self.content_container = tk.Frame(body_frame, bg=BG_APP)
        self.content_container.pack(side="right", fill="both", expand=True)

        # Instanciação das views
        self.views["dashboard"] = DashboardView(self.content_container, on_navigate=self.mostrar_aba)
        self.views["produtos"] = ProdutosView(self.content_container, on_update_callback=self._ao_atualizar_dados)
        self.views["vendas"] = VendasView(self.content_container)

        if Session.is_admin():
            self.views["usuarios"] = UsuariosView(self.content_container, on_update_callback=self._ao_atualizar_dados)

    def _adicionar_botao_sidebar(self, chave: str, texto: str, comando: Callable):
        btn = tk.Button(
            self.sidebar,
            text=texto,
            bg=BG_SIDEBAR,
            fg="#cbd5e1",
            activebackground=BG_SIDEBAR_HOVER,
            activeforeground="#ffffff",
            font=("Segoe UI", 10),
            bd=0,
            padx=14,
            pady=10,
            anchor="w",
            cursor="hand2",
            command=comando
        )
        btn.pack(fill="x", pady=2)
        self.botoes_sidebar[chave] = btn

    def mostrar_aba(self, chave: str):
        """Alterna a exibição da tela central para a aba especificada."""
        if chave not in self.views:
            return

        if self.aba_atual and self.aba_atual in self.views:
            self.views[self.aba_atual].pack_forget()

        # Atualiza destaque moderno dos botões
        for k, btn in self.botoes_sidebar.items():
            if k == chave:
                btn.config(bg=PRIMARY, fg="#ffffff", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg=BG_SIDEBAR, fg="#cbd5e1", font=("Segoe UI", 10))

        self.aba_atual = chave
        self.views[chave].pack(fill="both", expand=True)

        if chave == "dashboard" and hasattr(self.views["dashboard"], "atualizar_metricas"):
            self.views["dashboard"].atualizar_metricas()
        elif chave == "produtos" and hasattr(self.views["produtos"], "carregar_produtos"):
            self.views["produtos"].carregar_produtos()

    def _ao_atualizar_dados(self):
        """Notifica o dashboard quando novos produtos ou usuários forem cadastrados/alterados."""
        if "dashboard" in self.views and hasattr(self.views["dashboard"], "atualizar_metricas"):
            self.views["dashboard"].atualizar_metricas()

    def _confirmar_logout(self):
        resposta = messagebox.askyesno(
            "Encerrar Sessão",
            "Deseja realmente sair da sua conta?",
            parent=self
        )
        if resposta:
            Session.clear()
            self.on_logout()
