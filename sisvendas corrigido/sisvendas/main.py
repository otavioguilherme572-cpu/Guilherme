"""
Ponto de Entrada Principal - SisVendas Desktop
Inicia o banco de dados e abre a interface gráfica com tela de login, painel principal e cadastro de produtos.
Compatível com Python 3.10, 3.11, 3.12, 3.13, 3.14 e 3.15.
"""
import sys
from pathlib import Path

# Garante o diretório raiz no PATH
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    import tkinter as tk
except ImportError:
    print("\n[ERRO] O módulo Tkinter não está instalado no seu ambiente Python.")
    print("No Windows: Ao instalar o Python, marque a opção 'tcl/tk and IDLE'.")
    print("No Linux: Execute 'sudo apt install python3-tk' ou 'sudo apt install python3.11-tk'.\n")
    sys.exit(1)

from ui.app import SisVendasApp


def main():
    app = SisVendasApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistema encerrado pelo usuário.")
        sys.exit(0)
