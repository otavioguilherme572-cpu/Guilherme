import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from modules.auth import autenticar_usuario
from modules.usuarios import cadastrar_usuario
from ui.theme import (
    BG_APP, BG_CARD, PRIMARY, PRIMARY_HOVER, PRIMARY_LIGHT,
    SUCCESS, SUCCESS_HOVER, TEXT_DARK, TEXT_BODY, TEXT_MUTED,
    TEXT_LIGHT, BORDER_LIGHT, BORDER_COLOR, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_BOLD, FONT_SMALL
)


class LoginView(tk.Frame):
    """
    Tela de Autenticação e Cadastro com visual moderno estilo SaaS.
    Apresentada em formato de cartão centralizado.
    """
    def __init__(self, parent: tk.Widget, on_login_success: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, bg=BG_APP)
        self.on_login_success = on_login_success

        self._criar_layout()
        self.mostrar_login()

    def _criar_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Cartão Central Flutuante
        self.card = tk.Frame(
            self,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            highlightthickness=0,
            padx=40,
            pady=35
        )
        self.card.grid(row=0, column=0)

        # Badge do Ícone
        badge_frame = tk.Frame(self.card, bg=PRIMARY_LIGHT, padx=12, pady=6)
        badge_frame.pack(pady=(0, 10))

        lbl_icone = tk.Label(
            badge_frame,
            text="🛒",
            bg=PRIMARY_LIGHT,
            font=("Segoe UI", 22)
        )
        lbl_icone.pack()

        # Cabeçalho do Cartão
        lbl_logo = tk.Label(
            self.card,
            text="SISVENDAS",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=("Segoe UI", 18, "bold")
        )
        lbl_logo.pack(pady=(0, 2))

        self.lbl_subtitulo = tk.Label(
            self.card,
            text="Sistema de Gestão Comercial e PDV",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        self.lbl_subtitulo.pack(pady=(0, 18))

        # Divisor Sutil
        divisor = tk.Frame(self.card, bg=BORDER_LIGHT, height=1, width=320)
        divisor.pack(fill="x", pady=(0, 18))

        # Container Dinâmico do Formulário
        self.form_frame = tk.Frame(self.card, bg=BG_CARD)
        self.form_frame.pack(fill="both", expand=True)

    def mostrar_login(self):
        """Renderiza o formulário de login."""
        self._limpar_form()
        self.lbl_subtitulo.config(text="Informe suas credenciais para acessar")

        # Campo Usuário
        lbl_user = tk.Label(self.form_frame, text="Usuário:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_user.pack(fill="x", pady=(0, 3))
        self.ent_user = ttk.Entry(self.form_frame, font=FONT_BODY, width=32)
        self.ent_user.pack(fill="x", pady=(0, 14), ipady=2)
        self.ent_user.focus_set()

        # Campo Senha
        lbl_pass = tk.Label(self.form_frame, text="Senha:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_pass.pack(fill="x", pady=(0, 3))
        self.ent_pass = ttk.Entry(self.form_frame, font=FONT_BODY, show="•", width=32)
        self.ent_pass.pack(fill="x", pady=(0, 18), ipady=2)

        # Enter nos campos
        self.ent_user.bind("<Return>", lambda e: self.ent_pass.focus_set())
        self.ent_pass.bind("<Return>", lambda e: self._processar_login())

        # Botão Entrar
        btn_login = ttk.Button(
            self.form_frame,
            text="Entrar no Sistema",
            style="Primary.TButton",
            command=self._processar_login
        )
        btn_login.pack(fill="x", pady=(0, 14))

        # Alternar para Cadastro
        lbl_ou = tk.Label(self.form_frame, text="Ainda não tem acesso?", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL)
        lbl_ou.pack(pady=(6, 2))

        btn_cadastro = tk.Button(
            self.form_frame,
            text="Criar novo usuário",
            bg=BG_CARD,
            fg=PRIMARY,
            activebackground=BG_CARD,
            activeforeground=PRIMARY_HOVER,
            font=FONT_BOLD,
            bd=0,
            cursor="hand2",
            command=self.mostrar_cadastro
        )
        btn_cadastro.pack()

        # Caixa com dica de credencial padrão
        dica_box = tk.Frame(self.form_frame, bg="#f8fafc", bd=1, relief="solid", padx=10, pady=6)
        dica_box.pack(fill="x", pady=(18, 0))

        lbl_dica = tk.Label(
            dica_box,
            text="🔑 Acesso Padrão: admin  |  Senha: admin123",
            bg="#f8fafc",
            fg=TEXT_MUTED,
            font=("Segoe UI", 8)
        )
        lbl_dica.pack()

    def mostrar_cadastro(self):
        """Renderiza o formulário de cadastro de novo usuário."""
        self._limpar_form()
        self.lbl_subtitulo.config(text="Preencha os dados do novo operador")

        # Campo Nome Completo
        lbl_nome = tk.Label(self.form_frame, text="Nome Completo:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_nome.pack(fill="x", pady=(0, 2))
        self.ent_cad_nome = ttk.Entry(self.form_frame, font=FONT_BODY, width=32)
        self.ent_cad_nome.pack(fill="x", pady=(0, 10), ipady=2)
        self.ent_cad_nome.focus_set()

        # Campo Login
        lbl_user = tk.Label(self.form_frame, text="Usuário (Login):", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_user.pack(fill="x", pady=(0, 2))
        self.ent_cad_user = ttk.Entry(self.form_frame, font=FONT_BODY, width=32)
        self.ent_cad_user.pack(fill="x", pady=(0, 10), ipady=2)

        # Campo Cargo
        lbl_cargo = tk.Label(self.form_frame, text="Cargo / Nível de Acesso:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_cargo.pack(fill="x", pady=(0, 2))
        self.cmb_cad_cargo = ttk.Combobox(
            self.form_frame,
            values=["Vendedor", "Administrador"],
            state="readonly",
            font=FONT_BODY
        )
        self.cmb_cad_cargo.set("Vendedor")
        self.cmb_cad_cargo.pack(fill="x", pady=(0, 10))

        # Campo Senha
        lbl_pass = tk.Label(self.form_frame, text="Senha:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_pass.pack(fill="x", pady=(0, 2))
        self.ent_cad_pass = ttk.Entry(self.form_frame, font=FONT_BODY, show="•", width=32)
        self.ent_cad_pass.pack(fill="x", pady=(0, 10), ipady=2)

        # Confirmar Senha
        lbl_pass2 = tk.Label(self.form_frame, text="Confirmar Senha:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD, anchor="w")
        lbl_pass2.pack(fill="x", pady=(0, 2))
        self.ent_cad_pass2 = ttk.Entry(self.form_frame, font=FONT_BODY, show="•", width=32)
        self.ent_cad_pass2.pack(fill="x", pady=(0, 14), ipady=2)

        # Botão Confirmar
        btn_salvar = ttk.Button(
            self.form_frame,
            text="Confirmar Cadastro",
            style="Success.TButton",
            command=self._processar_cadastro
        )
        btn_salvar.pack(fill="x", pady=(0, 10))

        # Botão Voltar
        btn_voltar = tk.Button(
            self.form_frame,
            text="← Voltar para o Login",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            activebackground=BG_CARD,
            activeforeground=TEXT_DARK,
            font=FONT_BODY,
            bd=0,
            cursor="hand2",
            command=self.mostrar_login
        )
        btn_voltar.pack()

    def _limpar_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def _processar_login(self):
        usuario = self.ent_user.get().strip()
        senha = self.ent_pass.get()

        if not usuario or not senha:
            messagebox.showwarning("Atenção", "Por favor, informe seu usuário e senha.", parent=self)
            return

        sucesso, msg = autenticar_usuario(usuario, senha)
        if sucesso:
            self.on_login_success()
        else:
            messagebox.showerror("Erro de Autenticação", msg, parent=self)
            self.ent_pass.delete(0, tk.END)
            self.ent_pass.focus_set()

    def _processar_cadastro(self):
        nome = self.ent_cad_nome.get().strip()
        usuario = self.ent_cad_user.get().strip()
        cargo = self.cmb_cad_cargo.get()
        senha = self.ent_cad_pass.get()
        confirma_senha = self.ent_cad_pass2.get()

        if not nome or not usuario or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.", parent=self)
            return

        if senha != confirma_senha:
            messagebox.showerror("Erro", "As senhas digitadas não coincidem.", parent=self)
            return

        sucesso, msg = cadastrar_usuario(nome, usuario, senha, cargo, ativo=1)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Usuário '{usuario}' cadastrado com sucesso!\nVocê já pode fazer login.", parent=self)
            self.mostrar_login()
            self.ent_user.insert(0, usuario)
            self.ent_pass.focus_set()
        else:
            messagebox.showerror("Erro no Cadastro", msg, parent=self)
