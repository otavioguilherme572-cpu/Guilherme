import tkinter as tk
from database.connection import init_db
from modules.auth import criar_usuario_admin_padrao, Session
from ui.theme import apply_theme, BG_APP
from ui.login_view import LoginView
from ui.main_view import MainView


class SisVendasApp:
    """
    Controlador Principal da Aplicação Gráfica Desktop.
    Gerencia a janela raiz, alternância de telas (Login <-> Painel Principal) e ciclo de vida.
    """
    def __init__(self):
        # 1. Garante inicialização do banco de dados e usuário admin
        init_db()
        criar_usuario_admin_padrao()

        # 2. Inicializa a janela raiz do Tkinter
        self.root = tk.Tk()
        self.root.title("SisVendas - Sistema de Gestão Comercial")
        self.root.configure(bg=BG_APP)

        # Configura tamanho inicial e centraliza na tela
        largura = 1180
        altura = 720
        self.root.minsize(980, 620)
        self._centralizar_janela(largura, altura)

        # 3. Aplica estilos e temas
        apply_theme(self.root)

        # Frame de container principal
        self.current_view = None

        # 4. Inicia pela tela de Login
        self.mostrar_login()

    def _centralizar_janela(self, largura: int, altura: int):
        tela_largura = self.root.winfo_screenwidth()
        tela_altura = self.root.winfo_screenheight()
        pos_x = max(0, (tela_largura - largura) // 2)
        pos_y = max(0, (tela_altura - altura) // 2)
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def mostrar_login(self):
        """Exibe a tela de login/cadastro de usuário."""
        if self.current_view:
            self.current_view.destroy()

        self.root.title("SisVendas - Login")
        self.current_view = LoginView(
            self.root,
            on_login_success=self.mostrar_painel_principal
        )
        self.current_view.pack(fill="both", expand=True)

    def mostrar_painel_principal(self):
        """Exibe o painel principal após autenticação bem-sucedida."""
        if self.current_view:
            self.current_view.destroy()

        nome_usuario = Session.nome or Session.usuario or "Usuário"
        self.root.title(f"SisVendas - Painel Principal [{nome_usuario}]")

        self.current_view = MainView(
            self.root,
            on_logout=self.mostrar_login
        )
        self.current_view.pack(fill="both", expand=True)

    def run(self):
        """Inicia o loop principal de eventos da interface gráfica."""
        self.root.mainloop()

