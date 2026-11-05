import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import (
    BG_APP, BG_CARD, PRIMARY, PRIMARY_LIGHT, SUCCESS, TEXT_DARK,
    TEXT_BODY, TEXT_MUTED, BORDER_LIGHT, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_BOLD
)


class VendasView(tk.Frame):
    """
    Interface do Módulo de Vendas (PDV - Ponto de Venda) com visual moderno.
    """
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=BG_APP)
        self._criar_layout()

    def _criar_layout(self):
        header = tk.Frame(self, bg=BG_APP)
        header.pack(fill="x", padx=25, pady=(22, 16))

        lbl_titulo = tk.Label(
            header,
            text="🛒 Frente de Caixa / Vendas (PDV)",
            bg=BG_APP,
            fg=TEXT_DARK,
            font=FONT_TITLE
        )
        lbl_titulo.pack(anchor="w")

        # Cartão Informativo
        card = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid", padx=35, pady=35)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        # Badge do Ícone
        badge = tk.Frame(card, bg=PRIMARY_LIGHT, padx=16, pady=12)
        badge.pack(pady=(15, 12))

        lbl_icone = tk.Label(badge, text="💳", bg=PRIMARY_LIGHT, font=("Segoe UI", 32))
        lbl_icone.pack()

        lbl_status = tk.Label(
            card,
            text="Módulo de Caixa Pronto para Ativação",
            bg=BG_CARD,
            fg=TEXT_DARK,
            font=FONT_SUBTITLE
        )
        lbl_status.pack(pady=(0, 8))

        lbl_desc = tk.Label(
            card,
            text=(
                "A estrutura relacional das tabelas de vendas e itens já está integrada ao SQLite.\n"
                "Os produtos e operadores cadastrados estão disponíveis para consulta e movimentação.\n\n"
                "Recursos previstos nesta frente:\n"
                "• Leitura de código de barras USB com beep sonoro\n"
                "• Lançamento de itens na comanda e cálculo dinâmico de troco\n"
                "• Baixa automática no estoque ao finalizar a transação\n"
                "• Múltiplas formas de pagamento: Pix, Cartão de Crédito/Débito e Dinheiro\n"
                "• Impressão de comprovante não fiscal"
            ),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=FONT_BODY,
            justify="center"
        )
        lbl_desc.pack(pady=(0, 24))

        btn_teste = ttk.Button(
            card,
            text="Simular Frente de Caixa",
            style="Primary.TButton",
            command=lambda: messagebox.showinfo(
                "PDV SisVendas",
                "O catálogo de produtos já está abastecido e pronto!\n"
                "Para gerenciar os itens disponíveis, acesse a aba 'Produtos & Estoque'.",
                parent=self
            )
        )
        btn_teste.pack()
