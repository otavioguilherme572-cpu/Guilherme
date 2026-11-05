import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from modules.usuarios import (
    listar_usuarios,
    cadastrar_usuario,
    atualizar_status_usuario
)
from modules.auth import Session
from ui.theme import (
    BG_APP, BG_CARD, PRIMARY, SUCCESS, DANGER, TEXT_DARK,
    TEXT_BODY, TEXT_MUTED, TEXT_LIGHT, BORDER_LIGHT, FONT_TITLE,
    FONT_SUBTITLE, FONT_BODY, FONT_BOLD, FONT_SMALL
)


class UsuariosView(tk.Frame):
    """
    Interface para Gerenciamento de Usuários e Permissões com paleta moderna.
    """
    def __init__(self, parent: tk.Widget, on_update_callback: Optional[Callable] = None):
        super().__init__(parent, bg=BG_APP)
        self.on_update_callback = on_update_callback

        self._criar_layout()
        self.carregar_usuarios()

    def _criar_layout(self):
        # Topo
        header = tk.Frame(self, bg=BG_APP)
        header.pack(fill="x", padx=22, pady=(18, 12))

        lbl_titulo = tk.Label(
            header,
            text="👥 Gestão de Usuários e Permissões",
            bg=BG_APP,
            fg=TEXT_DARK,
            font=FONT_TITLE
        )
        lbl_titulo.pack(side="left")

        # Barra de Pesquisa
        search_frame = tk.Frame(header, bg=BG_APP)
        search_frame.pack(side="right")

        self.ent_busca = ttk.Entry(search_frame, width=24, font=FONT_BODY)
        self.ent_busca.pack(side="left", padx=(0, 6), ipady=3)
        self.ent_busca.bind("<Return>", lambda e: self.carregar_usuarios())

        btn_buscar = ttk.Button(
            search_frame,
            text="🔍 Buscar",
            style="Primary.TButton",
            command=self.carregar_usuarios
        )
        btn_buscar.pack(side="left", padx=(0, 6))

        # Conteúdo Principal: Split
        content_frame = tk.Frame(self, bg=BG_APP)
        content_frame.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        # Painel Esquerdo: Formulário
        form_card = tk.Frame(
            content_frame,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            width=320,
            padx=20,
            pady=16
        )
        form_card.pack(side="left", fill="y", padx=(0, 16))
        form_card.pack_propagate(False)

        lbl_form_tit = tk.Label(
            form_card,
            text="👤 Novo Usuário",
            bg=BG_CARD,
            fg=PRIMARY,
            font=FONT_SUBTITLE
        )
        lbl_form_tit.pack(anchor="w", pady=(0, 3))

        lbl_form_desc = tk.Label(
            form_card,
            text="Cadastre um novo operador para o sistema",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        lbl_form_desc.pack(anchor="w", pady=(0, 12))

        tk.Frame(form_card, bg=BORDER_LIGHT, height=1).pack(fill="x", pady=(0, 12))

        # Nome
        lbl_nome = tk.Label(form_card, text="Nome Completo *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_nome.pack(anchor="w", pady=(0, 2))
        self.ent_nome = ttk.Entry(form_card, font=FONT_BODY)
        self.ent_nome.pack(fill="x", pady=(0, 8), ipady=2)

        # Login
        lbl_user = tk.Label(form_card, text="Usuário (Login) *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_user.pack(anchor="w", pady=(0, 2))
        self.ent_user = ttk.Entry(form_card, font=FONT_BODY)
        self.ent_user.pack(fill="x", pady=(0, 8), ipady=2)

        # Cargo
        lbl_cargo = tk.Label(form_card, text="Cargo / Nível:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_cargo.pack(anchor="w", pady=(0, 2))
        self.cmb_cargo = ttk.Combobox(form_card, values=["Vendedor", "Administrador"], state="readonly", font=FONT_BODY)
        self.cmb_cargo.set("Vendedor")
        self.cmb_cargo.pack(fill="x", pady=(0, 8))

        # Senha
        lbl_pass = tk.Label(form_card, text="Senha Inicial *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_pass.pack(anchor="w", pady=(0, 2))
        self.ent_pass = ttk.Entry(form_card, font=FONT_BODY, show="•")
        self.ent_pass.pack(fill="x", pady=(0, 8), ipady=2)

        # Confirmar Senha
        lbl_pass2 = tk.Label(form_card, text="Confirmar Senha *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_pass2.pack(anchor="w", pady=(0, 2))
        self.ent_pass2 = ttk.Entry(form_card, font=FONT_BODY, show="•")
        self.ent_pass2.pack(fill="x", pady=(0, 15), ipady=2)

        # Botão Salvar
        btn_salvar = ttk.Button(
            form_card,
            text="➕ Cadastrar Usuário",
            style="Success.TButton",
            command=self._salvar_usuario
        )
        btn_salvar.pack(fill="x", pady=(0, 8))

        btn_limpar = ttk.Button(
            form_card,
            text="Limpar Campos",
            style="Secondary.TButton",
            command=self._limpar_form
        )
        btn_limpar.pack(fill="x")

        # Painel Direito: Tabela
        table_card = tk.Frame(
            content_frame,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=12
        )
        table_card.pack(side="right", fill="both", expand=True)

        top_table = tk.Frame(table_card, bg=BG_CARD)
        top_table.pack(fill="x", pady=(0, 10))

        self.lbl_total = tk.Label(
            top_table,
            text="Carregando usuários...",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=FONT_BOLD
        )
        self.lbl_total.pack(side="left")

        self.btn_toggle_status = ttk.Button(
            top_table,
            text="Alternar Status (Ativo/Inativo)",
            style="Secondary.TButton",
            command=self._alternar_status_selecionado
        )
        self.btn_toggle_status.pack(side="right")

        # Treeview
        tree_container = tk.Frame(table_card, bg=BG_CARD)
        tree_container.pack(fill="both", expand=True)

        colunas = ("id", "nome", "usuario", "cargo", "status", "criado_em")
        self.tree = ttk.Treeview(
            tree_container,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome Completo")
        self.tree.heading("usuario", text="Usuário (Login)")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("status", text="Status")
        self.tree.heading("criado_em", text="Data Cadastro")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("nome", width=200, anchor="w")
        self.tree.column("usuario", width=120, anchor="w")
        self.tree.column("cargo", width=110, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("criado_em", width=140, anchor="center")

        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.tag_configure("par", background="#ffffff")
        self.tree.tag_configure("impar", background="#f8fafc")
        self.tree.tag_configure("inativo", foreground="#94a3b8")

    def carregar_usuarios(self):
        termo = self.ent_busca.get().strip()
        usuarios = listar_usuarios(termo_busca=termo)

        for item in self.tree.get_children():
            self.tree.delete(item)

        total_ativos = 0
        for idx, u in enumerate(usuarios):
            status_txt = "Ativo" if u["ativo"] == 1 else "Inativo"
            if u["ativo"] == 1:
                total_ativos += 1

            tag = "inativo" if u["ativo"] == 0 else ("impar" if idx % 2 == 1 else "par")

            self.tree.insert(
                "",
                "end",
                iid=str(u["id"]),
                values=(
                    u["id"],
                    u["nome"],
                    u["usuario"],
                    u["cargo"],
                    status_txt,
                    u["criado_em"] or "-"
                ),
                tags=(tag,)
            )

        self.lbl_total.config(
            text=f"Total: {len(usuarios)} usuário(s) • {total_ativos} ativo(s)"
        )

        if self.on_update_callback:
            self.on_update_callback()

    def _salvar_usuario(self):
        nome = self.ent_nome.get().strip()
        usuario = self.ent_user.get().strip()
        cargo = self.cmb_cargo.get()
        senha = self.ent_pass.get()
        confirma = self.ent_pass2.get()

        if not nome or not usuario or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.", parent=self)
            return

        if senha != confirma:
            messagebox.showerror("Erro", "As senhas digitadas não conferem.", parent=self)
            return

        sucesso, msg = cadastrar_usuario(nome, usuario, senha, cargo, ativo=1)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self._limpar_form()
            self.carregar_usuarios()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _alternar_status_selecionado(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showinfo("Aviso", "Selecione um usuário na tabela para alterar o status.", parent=self)
            return

        user_id = int(selecionados[0])
        valores = self.tree.item(str(user_id))["values"]
        nome = valores[1]
        login = valores[2]
        status_atual = valores[4]

        if login == "admin" and status_atual == "Ativo":
            messagebox.showwarning("Operação Não Permitida", "O usuário administrador padrão 'admin' não pode ser desativado.", parent=self)
            return

        novo_status = 0 if status_atual == "Ativo" else 1
        acao = "desativar" if status_atual == "Ativo" else "ativar"

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Deseja realmente {acao} o usuário '{nome}' ({login})?",
            parent=self
        )
        if not confirmar:
            return

        sucesso, msg = atualizar_status_usuario(user_id, novo_status)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.carregar_usuarios()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _limpar_form(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_user.delete(0, tk.END)
        self.ent_pass.delete(0, tk.END)
        self.ent_pass2.delete(0, tk.END)
        self.cmb_cargo.set("Vendedor")
