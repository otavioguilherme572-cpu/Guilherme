import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import Optional, Callable

from modules.produtos import (
    cadastrar_produto,
    atualizar_produto,
    excluir_ou_desativar_produto,
    listar_produtos,
    obter_produto_por_id,
    metricas_produtos
)
from ui.theme import (
    BG_APP, BG_CARD, BG_CARD_ALT, PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_HOVER,
    DANGER, DANGER_HOVER, DANGER_LIGHT, WARNING, TEXT_DARK, TEXT_BODY,
    TEXT_MUTED, TEXT_LIGHT, BORDER_LIGHT, BORDER_COLOR, FONT_TITLE,
    FONT_SUBTITLE, FONT_SECTION, FONT_BODY, FONT_BOLD, FONT_SMALL
)


class ProdutosView(tk.Frame):
    """
    Interface Gráfica para Cadastro e Gerenciamento de Produtos e Estoque.
    Contém formulário de cadastro/edição e tabela com busca, paginação e zebra striping.
    """
    def __init__(self, parent: tk.Widget, on_update_callback: Optional[Callable] = None):
        super().__init__(parent, bg=BG_APP)
        self.on_update_callback = on_update_callback
        self.produto_selecionado_id: Optional[int] = None

        self._criar_layout()
        self.carregar_produtos()

    def _criar_layout(self):
        # Topo da View: Título e Barra de Busca
        header_frame = tk.Frame(self, bg=BG_APP)
        header_frame.pack(fill="x", padx=22, pady=(18, 12))

        lbl_titulo = tk.Label(
            header_frame,
            text="📦 Cadastro e Gestão de Produtos",
            bg=BG_APP,
            fg=TEXT_DARK,
            font=FONT_TITLE
        )
        lbl_titulo.pack(side="left")

        # Barra de Pesquisa
        search_frame = tk.Frame(header_frame, bg=BG_APP)
        search_frame.pack(side="right")

        self.ent_busca = ttk.Entry(search_frame, width=28, font=FONT_BODY)
        self.ent_busca.pack(side="left", padx=(0, 6), ipady=3)
        self.ent_busca.bind("<Return>", lambda e: self.carregar_produtos())

        btn_buscar = ttk.Button(
            search_frame,
            text="🔍 Buscar",
            style="Primary.TButton",
            command=self.carregar_produtos
        )
        btn_buscar.pack(side="left", padx=(0, 6))

        btn_limpar_busca = ttk.Button(
            search_frame,
            text="Limpar Filtro",
            style="Secondary.TButton",
            command=self._limpar_busca
        )
        btn_limpar_busca.pack(side="left")

        # Conteúdo Principal: Split (Formulário à Esquerda, Tabela à Direita)
        content_frame = tk.Frame(self, bg=BG_APP)
        content_frame.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        # =====================================================================
        # PAINEL ESQUERDO: FORMULÁRIO DE CADASTRO / EDIÇÃO
        # =====================================================================
        self.form_card = tk.Frame(
            content_frame,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            width=360,
            padx=20,
            pady=16
        )
        self.form_card.pack(side="left", fill="y", padx=(0, 16))
        self.form_card.pack_propagate(False)

        self.lbl_form_titulo = tk.Label(
            self.form_card,
            text="✨ Novo Produto",
            bg=BG_CARD,
            fg=PRIMARY,
            font=FONT_SUBTITLE
        )
        self.lbl_form_titulo.pack(anchor="w", pady=(0, 3))

        self.lbl_form_modo = tk.Label(
            self.form_card,
            text="Preencha os campos para cadastrar no catálogo",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        self.lbl_form_modo.pack(anchor="w", pady=(0, 12))

        # Divisor
        tk.Frame(self.form_card, bg=BORDER_LIGHT, height=1).pack(fill="x", pady=(0, 12))

        # Código de Barras
        lbl_cb = tk.Label(self.form_card, text="Código de Barras:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_cb.pack(anchor="w", pady=(0, 2))

        cb_row = tk.Frame(self.form_card, bg=BG_CARD)
        cb_row.pack(fill="x", pady=(0, 8))

        self.ent_codigo = ttk.Entry(cb_row, font=FONT_BODY)
        self.ent_codigo.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=2)

        btn_gerar_cb = ttk.Button(
            cb_row,
            text="Gerar",
            style="Secondary.TButton",
            command=self._gerar_codigo_aleatorio
        )
        btn_gerar_cb.pack(side="right")

        # Nome do Produto
        lbl_nome = tk.Label(self.form_card, text="Nome do Produto *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_nome.pack(anchor="w", pady=(0, 2))
        self.ent_nome = ttk.Entry(self.form_card, font=FONT_BODY)
        self.ent_nome.pack(fill="x", pady=(0, 8), ipady=2)

        # Preços (Custo e Venda em linha dupla)
        precos_frame = tk.Frame(self.form_card, bg=BG_CARD)
        precos_frame.pack(fill="x", pady=(0, 8))

        # Preço Custo
        col_custo = tk.Frame(precos_frame, bg=BG_CARD)
        col_custo.pack(side="left", fill="x", expand=True, padx=(0, 6))
        lbl_custo = tk.Label(col_custo, text="Preço Custo (R$):", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_custo.pack(anchor="w", pady=(0, 2))
        self.ent_custo = ttk.Entry(col_custo, font=FONT_BODY)
        self.ent_custo.pack(fill="x", ipady=2)
        self.ent_custo.insert(0, "0.00")
        self.ent_custo.bind("<KeyRelease>", lambda e: self._calcular_margem())

        # Preço Venda
        col_venda = tk.Frame(precos_frame, bg=BG_CARD)
        col_venda.pack(side="right", fill="x", expand=True)
        lbl_venda = tk.Label(col_venda, text="Preço Venda (R$) *:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_venda.pack(anchor="w", pady=(0, 2))
        self.ent_venda = ttk.Entry(col_venda, font=FONT_BODY)
        self.ent_venda.pack(fill="x", ipady=2)
        self.ent_venda.insert(0, "0.00")
        self.ent_venda.bind("<KeyRelease>", lambda e: self._calcular_margem())

        # Indicador de Margem de Lucro Calculada
        self.lbl_margem = tk.Label(
            self.form_card,
            text="Margem estimada: R$ 0,00 (0.0%)",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8, "italic")
        )
        self.lbl_margem.pack(anchor="w", pady=(0, 8))

        # Estoque e Status (linha dupla)
        estoque_frame = tk.Frame(self.form_card, bg=BG_CARD)
        estoque_frame.pack(fill="x", pady=(0, 14))

        # Qtd Estoque
        col_est = tk.Frame(estoque_frame, bg=BG_CARD)
        col_est.pack(side="left", fill="x", expand=True, padx=(0, 6))
        lbl_est = tk.Label(col_est, text="Estoque Inicial:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_est.pack(anchor="w", pady=(0, 2))
        self.ent_estoque = ttk.Entry(col_est, font=FONT_BODY)
        self.ent_estoque.pack(fill="x", ipady=2)
        self.ent_estoque.insert(0, "0")

        # Status
        col_status = tk.Frame(estoque_frame, bg=BG_CARD)
        col_status.pack(side="right", fill="x", expand=True)
        lbl_status = tk.Label(col_status, text="Status:", bg=BG_CARD, fg=TEXT_BODY, font=FONT_BOLD)
        lbl_status.pack(anchor="w", pady=(0, 2))
        self.cmb_status = ttk.Combobox(col_status, values=["Ativo", "Inativo"], state="readonly", font=FONT_BODY)
        self.cmb_status.set("Ativo")
        self.cmb_status.pack(fill="x")

        # Botões de Ação do Formulário
        self.btn_salvar = ttk.Button(
            self.form_card,
            text="💾 Salvar Produto",
            style="Success.TButton",
            command=self._salvar_produto
        )
        self.btn_salvar.pack(fill="x", pady=(8, 6))

        self.btn_limpar = ttk.Button(
            self.form_card,
            text="Novo / Limpar Formulário",
            style="Secondary.TButton",
            command=self.limpar_formulario
        )
        self.btn_limpar.pack(fill="x", pady=(0, 6))

        self.btn_excluir = ttk.Button(
            self.form_card,
            text="🗑️ Excluir / Desativar",
            style="Danger.TButton",
            command=self._excluir_produto
        )
        self.btn_excluir.pack(fill="x")
        self.btn_excluir.config(state="disabled")

        # =====================================================================
        # PAINEL DIREITO: TABELA DE PRODUTOS CADASTRADOS
        # =====================================================================
        table_card = tk.Frame(
            content_frame,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=12
        )
        table_card.pack(side="right", fill="both", expand=True)

        # Informações da Tabela
        info_row = tk.Frame(table_card, bg=BG_CARD)
        info_row.pack(fill="x", pady=(0, 10))

        self.lbl_total_tabela = tk.Label(
            info_row,
            text="Carregando produtos...",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=FONT_BOLD
        )
        self.lbl_total_tabela.pack(side="left")

        lbl_ajuda = tk.Label(
            info_row,
            text="💡 Dica: Dê dois cliques na linha para editar",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        lbl_ajuda.pack(side="right")

        # Treeview + Scrollbars
        tree_container = tk.Frame(table_card, bg=BG_CARD)
        tree_container.pack(fill="both", expand=True)

        colunas = ("id", "codigo", "nome", "custo", "venda", "lucro", "estoque", "status")
        self.tree = ttk.Treeview(
            tree_container,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        # Cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Cód. Barras")
        self.tree.heading("nome", text="Nome do Produto")
        self.tree.heading("custo", text="Custo (R$)")
        self.tree.heading("venda", text="Venda (R$)")
        self.tree.heading("lucro", text="Margem")
        self.tree.heading("estoque", text="Estoque")
        self.tree.heading("status", text="Status")

        # Larguras e Alinhamentos
        self.tree.column("id", width=45, anchor="center")
        self.tree.column("codigo", width=120, anchor="center")
        self.tree.column("nome", width=220, anchor="w")
        self.tree.column("custo", width=85, anchor="e")
        self.tree.column("venda", width=85, anchor="e")
        self.tree.column("lucro", width=75, anchor="center")
        self.tree.column("estoque", width=70, anchor="center")
        self.tree.column("status", width=75, anchor="center")

        # Scrollbars
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Eventos da Tabela
        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)
        self.tree.bind("<Double-1>", lambda e: self._on_item_select(e))

        # Tags com cores refinadas para linhas alternadas e alertas
        self.tree.tag_configure("par", background="#ffffff")
        self.tree.tag_configure("impar", background="#f8fafc")
        self.tree.tag_configure("estoque_baixo", background=DANGER_LIGHT, foreground=DANGER)
        self.tree.tag_configure("inativo", foreground="#94a3b8")

    def _gerar_codigo_aleatorio(self):
        prefixo = "789"
        corpo = "".join([str(random.randint(0, 9)) for _ in range(10)])
        codigo = prefixo + corpo
        self.ent_codigo.delete(0, tk.END)
        self.ent_codigo.insert(0, codigo)

    def _calcular_margem(self):
        try:
            custo_str = self.ent_custo.get().replace(",", ".").strip()
            venda_str = self.ent_venda.get().replace(",", ".").strip()
            custo = float(custo_str) if custo_str else 0.0
            venda = float(venda_str) if venda_str else 0.0

            lucro_reais = venda - custo
            margem_pct = (lucro_reais / venda * 100) if venda > 0 else 0.0

            cor = SUCCESS if lucro_reais > 0 else (DANGER if lucro_reais < 0 else TEXT_MUTED)
            self.lbl_margem.config(
                text=f"Margem estimada: R$ {lucro_reais:.2f} ({margem_pct:.1f}%)",
                fg=cor
            )
        except ValueError:
            self.lbl_margem.config(text="Margem estimada: R$ 0,00 (0.0%)", fg=TEXT_MUTED)

    def carregar_produtos(self):
        termo = self.ent_busca.get().strip()
        produtos = listar_produtos(termo_busca=termo)

        for item in self.tree.get_children():
            self.tree.delete(item)

        total_ativos = 0
        total_estoque = 0

        for idx, prod in enumerate(produtos):
            custo = prod["preco_custo"]
            venda = prod["preco_venda"]
            estoque = prod["estoque"]
            status_txt = "Ativo" if prod["ativo"] == 1 else "Inativo"

            if prod["ativo"] == 1:
                total_ativos += 1
                total_estoque += estoque

            lucro_pct = f"{((venda - custo) / venda * 100):.0f}%" if venda > 0 else "0%"

            # Formatação de cores e zebra striping
            if prod["ativo"] == 0:
                tag = "inativo"
            elif estoque <= 5:
                tag = "estoque_baixo"
            else:
                tag = "impar" if idx % 2 == 1 else "par"

            self.tree.insert(
                "",
                "end",
                iid=str(prod["id"]),
                values=(
                    prod["id"],
                    prod["codigo_barras"] or "-",
                    prod["nome"],
                    f"R$ {custo:.2f}",
                    f"R$ {venda:.2f}",
                    lucro_pct,
                    estoque,
                    status_txt
                ),
                tags=(tag,)
            )

        self.lbl_total_tabela.config(
            text=f"Total: {len(produtos)} produto(s) • {total_ativos} ativo(s) • {total_estoque} unidades em estoque"
        )

        if self.on_update_callback:
            self.on_update_callback()

    def _limpar_busca(self):
        self.ent_busca.delete(0, tk.END)
        self.carregar_produtos()

    def _on_item_select(self, event=None):
        selecionados = self.tree.selection()
        if not selecionados:
            return

        prod_id = int(selecionados[0])
        prod = obter_produto_por_id(prod_id)
        if not prod:
            return

        self.produto_selecionado_id = prod["id"]
        self.lbl_form_titulo.config(text=f"✏️ Editar Produto #{prod['id']}", fg=WARNING)
        self.lbl_form_modo.config(text="Altere os dados e clique em Atualizar")

        self.ent_codigo.delete(0, tk.END)
        if prod["codigo_barras"]:
            self.ent_codigo.insert(0, prod["codigo_barras"])

        self.ent_nome.delete(0, tk.END)
        self.ent_nome.insert(0, prod["nome"])

        self.ent_custo.delete(0, tk.END)
        self.ent_custo.insert(0, f"{prod['preco_custo']:.2f}")

        self.ent_venda.delete(0, tk.END)
        self.ent_venda.insert(0, f"{prod['preco_venda']:.2f}")

        self.ent_estoque.delete(0, tk.END)
        self.ent_estoque.insert(0, str(prod["estoque"]))

        self.cmb_status.set("Ativo" if prod["ativo"] == 1 else "Inativo")

        self.btn_salvar.config(text="Atualizar Produto")
        self.btn_excluir.config(state="normal")
        self._calcular_margem()

    def limpar_formulario(self):
        self.produto_selecionado_id = None
        self.lbl_form_titulo.config(text="✨ Novo Produto", fg=PRIMARY)
        self.lbl_form_modo.config(text="Preencha os campos para cadastrar no catálogo")

        self.ent_codigo.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)
        self.ent_custo.delete(0, tk.END)
        self.ent_custo.insert(0, "0.00")
        self.ent_venda.delete(0, tk.END)
        self.ent_venda.insert(0, "0.00")
        self.ent_estoque.delete(0, tk.END)
        self.ent_estoque.insert(0, "0")
        self.cmb_status.set("Ativo")

        self.btn_salvar.config(text="💾 Salvar Produto")
        self.btn_excluir.config(state="disabled")
        self.tree.selection_remove(self.tree.selection())
        self._calcular_margem()

    def _salvar_produto(self):
        nome = self.ent_nome.get().strip()
        codigo_barras = self.ent_codigo.get().strip() or None
        custo_str = self.ent_custo.get().replace(",", ".").strip()
        venda_str = self.ent_venda.get().replace(",", ".").strip()
        estoque_str = self.ent_estoque.get().strip()
        ativo = 1 if self.cmb_status.get() == "Ativo" else 0

        try:
            custo = float(custo_str) if custo_str else 0.0
            venda = float(venda_str) if venda_str else 0.0
            estoque = int(estoque_str) if estoque_str else 0
        except ValueError:
            messagebox.showerror(
                "Valor Inválido",
                "Certifique-se de que Preço de Custo, Preço de Venda e Estoque são valores numéricos válidos.",
                parent=self
            )
            return

        if self.produto_selecionado_id is None:
            sucesso, msg, novo_id = cadastrar_produto(
                nome=nome,
                codigo_barras=codigo_barras,
                preco_custo=custo,
                preco_venda=venda,
                estoque=estoque,
                ativo=ativo
            )
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.limpar_formulario()
                self.carregar_produtos()
            else:
                messagebox.showerror("Erro no Cadastro", msg, parent=self)
        else:
            sucesso, msg = atualizar_produto(
                produto_id=self.produto_selecionado_id,
                nome=nome,
                codigo_barras=codigo_barras,
                preco_custo=custo,
                preco_venda=venda,
                estoque=estoque,
                ativo=ativo
            )
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.limpar_formulario()
                self.carregar_produtos()
            else:
                messagebox.showerror("Erro na Atualização", msg, parent=self)

    def _excluir_produto(self):
        if self.produto_selecionado_id is None:
            return

        nome = self.ent_nome.get()
        confirmacao = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir ou desativar o produto '{nome}'?",
            parent=self
        )
        if not confirmacao:
            return

        sucesso, msg = excluir_ou_desativar_produto(self.produto_selecionado_id)
        if sucesso:
            messagebox.showinfo("Resultado", msg, parent=self)
            self.limpar_formulario()
            self.carregar_produtos()
        else:
            messagebox.showerror("Erro", msg, parent=self)
