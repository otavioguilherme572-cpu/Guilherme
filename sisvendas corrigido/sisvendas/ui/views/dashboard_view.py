import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from modules.produtos import metricas_produtos, listar_produtos
from modules.usuarios import contar_usuarios
from modules.auth import Session
from ui.theme import (
    BG_APP, BG_CARD, PRIMARY, PRIMARY_LIGHT, SUCCESS, SUCCESS_LIGHT,
    WARNING, WARNING_LIGHT, DANGER, DANGER_LIGHT, INFO, INFO_LIGHT,
    TEXT_DARK, TEXT_BODY, TEXT_MUTED, TEXT_LIGHT, BORDER_LIGHT,
    FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY, FONT_BOLD,
    FONT_SMALL, FONT_STAT_NUM
)


class DashboardView(tk.Frame):
    """
    Painel Principal / Visão Geral do Sistema com estética moderna e cartões refinados.
    """
    def __init__(self, parent: tk.Widget, on_navigate: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=BG_APP)
        self.on_navigate = on_navigate

        self._criar_layout()
        self.atualizar_metricas()

    def _criar_layout(self):
        # Header do Dashboard
        header = tk.Frame(self, bg=BG_APP)
        header.pack(fill="x", padx=25, pady=(22, 16))

        lbl_bem_vindo = tk.Label(
            header,
            text=f"👋 Olá, {Session.nome or 'Usuário'}!",
            bg=BG_APP,
            fg=TEXT_DARK,
            font=FONT_TITLE
        )
        lbl_bem_vindo.pack(anchor="w")

        lbl_sub = tk.Label(
            header,
            text="Acompanhe os principais indicadores de estoque e operações da sua loja.",
            bg=BG_APP,
            fg=TEXT_MUTED,
            font=FONT_BODY
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Container dos Cartões de Métricas (Grid 4 colunas)
        cards_container = tk.Frame(self, bg=BG_APP)
        cards_container.pack(fill="x", padx=25, pady=(0, 22))
        for col in range(4):
            cards_container.grid_columnconfigure(col, weight=1, uniform="metric_cards")

        # Card 1: Produtos Ativos (Indigo)
        self.card_prod = self._criar_card_metrica(
            cards_container, 0,
            titulo="PRODUTOS ATIVOS",
            icone="📦",
            cor_destaque=PRIMARY,
            bg_icone=PRIMARY_LIGHT
        )

        # Card 2: Unidades em Estoque (Emerald)
        self.card_est = self._criar_card_metrica(
            cards_container, 1,
            titulo="UNIDADES EM ESTOQUE",
            icone="🏷️",
            cor_destaque=SUCCESS,
            bg_icone=SUCCESS_LIGHT
        )

        # Card 3: Estoque Crítico (Rose)
        self.card_baixo = self._criar_card_metrica(
            cards_container, 2,
            titulo="ESTOQUE CRÍTICO (≤ 5)",
            icone="⚠️",
            cor_destaque=DANGER,
            bg_icone=DANGER_LIGHT
        )

        # Card 4: Usuários do Sistema (Sky)
        self.card_users = self._criar_card_metrica(
            cards_container, 3,
            titulo="EQUIPE & OPERADORES",
            icone="👥",
            cor_destaque=INFO,
            bg_icone=INFO_LIGHT
        )

        # Seção Inferior: Atalhos Rápidos e Alertas
        bottom_frame = tk.Frame(self, bg=BG_APP)
        bottom_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Painel Esquerdo: Atalhos de Ação Rápida
        card_atalhos = tk.Frame(bottom_frame, bg=BG_CARD, bd=1, relief="solid", padx=20, pady=20, width=320)
        card_atalhos.pack(side="left", fill="y", padx=(0, 20))
        card_atalhos.pack_propagate(False)

        lbl_tit_atalhos = tk.Label(
            card_atalhos,
            text="⚡ Ações Rápidas",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=FONT_SUBTITLE
        )
        lbl_tit_atalhos.pack(anchor="w", pady=(0, 16))

        btn_cadastrar_prod = ttk.Button(
            card_atalhos,
            text="➕ Cadastrar Produto",
            style="Primary.TButton",
            command=lambda: self._navegar("produtos")
        )
        btn_cadastrar_prod.pack(fill="x", pady=(0, 10))

        btn_ir_vendas = ttk.Button(
            card_atalhos,
            text="🛒 Abrir Ponto de Venda (PDV)",
            style="Success.TButton",
            command=lambda: self._navegar("vendas")
        )
        btn_ir_vendas.pack(fill="x", pady=(0, 10))

        if Session.is_admin():
            btn_gerenciar_usuarios = ttk.Button(
                card_atalhos,
                text="👥 Gerenciar Usuários",
                style="Secondary.TButton",
                command=lambda: self._navegar("usuarios")
            )
            btn_gerenciar_usuarios.pack(fill="x", pady=(0, 10))

        btn_atualizar = ttk.Button(
            card_atalhos,
            text="🔄 Atualizar Indicadores",
            style="Secondary.TButton",
            command=self.atualizar_metricas
        )
        btn_atualizar.pack(fill="x", pady=(10, 0))

        # Painel Direito: Lista de Alertas de Estoque Crítico
        card_alertas = tk.Frame(bottom_frame, bg=BG_CARD, bd=1, relief="solid", padx=20, pady=16)
        card_alertas.pack(side="right", fill="both", expand=True)

        lbl_tit_alertas = tk.Label(
            card_alertas,
            text="⚠️ Produtos com Reposição Urgente (Estoque Baixo)",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=FONT_SUBTITLE
        )
        lbl_tit_alertas.pack(anchor="w", pady=(0, 12))

        # Tabela de Alertas de Estoque
        tree_frame = tk.Frame(card_alertas, bg=BG_CARD)
        tree_frame.pack(fill="both", expand=True)

        colunas = ("codigo", "nome", "estoque", "preco_venda")
        self.tree_alertas = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=6
        )
        self.tree_alertas.heading("codigo", text="Código")
        self.tree_alertas.heading("nome", text="Produto")
        self.tree_alertas.heading("estoque", text="Estoque Atual")
        self.tree_alertas.heading("preco_venda", text="Preço Venda")

        self.tree_alertas.column("codigo", width=110, anchor="center")
        self.tree_alertas.column("nome", width=240, anchor="w")
        self.tree_alertas.column("estoque", width=110, anchor="center")
        self.tree_alertas.column("preco_venda", width=110, anchor="e")

        scroll_alertas = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscrollcommand=scroll_alertas.set)
        scroll_alertas.pack(side="right", fill="y")
        self.tree_alertas.pack(side="left", fill="both", expand=True)

        self.tree_alertas.tag_configure("critico", background=DANGER_LIGHT, foreground=DANGER)

        self.lbl_rodape_alertas = tk.Label(
            card_alertas,
            text="",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        self.lbl_rodape_alertas.pack(anchor="w", pady=(8, 0))

    def _criar_card_metrica(self, parent: tk.Widget, col: int, titulo: str, icone: str, cor_destaque: str, bg_icone: str):
        card = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", padx=18, pady=16)
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        # Topo do card: Título e Badge de Ícone
        top_row = tk.Frame(card, bg=BG_CARD)
        top_row.pack(fill="x")

        lbl_tit = tk.Label(
            top_row,
            text=titulo,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9, "bold")
        )
        lbl_tit.pack(side="left")

        # Badge redondo/quadrado suave para o ícone
        badge = tk.Frame(top_row, bg=bg_icone, padx=6, pady=2)
        badge.pack(side="right")

        lbl_ico = tk.Label(
            badge,
            text=icone,
            bg=bg_icone,
            font=("Segoe UI", 12)
        )
        lbl_ico.pack()

        # Valor Principal
        lbl_val = tk.Label(
            card,
            text="0",
            bg=BG_CARD,
            fg=cor_destaque,
            font=FONT_STAT_NUM
        )
        lbl_val.pack(anchor="w", pady=(8, 0))

        # Legenda
        lbl_legenda = tk.Label(
            card,
            text="Atualizado",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8)
        )
        lbl_legenda.pack(anchor="w")

        return {"card": card, "val": lbl_val, "legenda": lbl_legenda}

    def atualizar_metricas(self):
        """Busca os números mais recentes do banco de dados e atualiza a interface."""
        metricas_p = metricas_produtos()
        dados_users = contar_usuarios()

        self.card_prod["val"].config(text=str(metricas_p["total_ativos"]))
        self.card_prod["legenda"].config(text=f"{metricas_p['total_produtos']} itens no catálogo")

        self.card_est["val"].config(text=str(metricas_p["total_unidades"]))
        self.card_est["legenda"].config(text=f"Total: R$ {metricas_p['valor_total_venda']:,.2f}")

        qtd_critica = metricas_p["estoque_baixo"] + metricas_p["estoque_zerado"]
        self.card_baixo["val"].config(text=str(qtd_critica))
        self.card_baixo["legenda"].config(
            text=f"{metricas_p['estoque_zerado']} zerados • {metricas_p['estoque_baixo']} baixos"
        )

        self.card_users["val"].config(text=str(dados_users["ativos"]))
        self.card_users["legenda"].config(text=f"{dados_users['total']} registrados")

        # Tabela de alertas
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)

        produtos = listar_produtos(apenas_ativos=True)
        produtos_criticos = [p for p in produtos if p["estoque"] <= 5]

        for p in produtos_criticos:
            self.tree_alertas.insert(
                "",
                "end",
                values=(
                    p["codigo_barras"] or "-",
                    p["nome"],
                    f"{p['estoque']} un",
                    f"R$ {p['preco_venda']:.2f}"
                ),
                tags=("critico",)
            )

        if produtos_criticos:
            self.lbl_rodape_alertas.config(
                text=f"⚠️ {len(produtos_criticos)} produto(s) precisam de reposição de estoque imediata.",
                fg=DANGER
            )
        else:
            self.lbl_rodape_alertas.config(
                text="✅ Excelente! Todos os produtos cadastrados estão com estoque regular.",
                fg=SUCCESS
            )

    def _navegar(self, aba: str):
        if self.on_navigate:
            self.on_navigate(aba)
