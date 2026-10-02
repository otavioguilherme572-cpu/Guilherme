import hashlib
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox

# ----------------- BANCO DE DADOS E SEGURANÇA ----------------- #

def init_db():
    """Inicializa o banco SQLite e cria a tabela de usuários."""
    with sqlite3.connect("sistema.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                salt BLOB NOT NULL,
                hash_senha BLOB NOT NULL
            )
        """)
        conn.commit()

def hash_senha(senha: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Gera salt e hash usando PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(16)
    chave = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=senha.encode("utf-8"),
        salt=salt,
        iterations=100_000
    )
    return salt, chave

def cadastrar_usuario(username: str, senha: str) -> tuple[bool, str]:
    if not username.strip() or not senha.strip():
        return False, "Usuário e senha não podem estar vazios."
    
    salt, senha_hasheada = hash_senha(senha)
    try:
        with sqlite3.connect("sistema.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, salt, hash_senha) VALUES (?, ?, ?)",
                (username.strip(), salt, senha_hasheada)
            )
            conn.commit()
            return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existe no sistema."
    except Exception as e:
        return False, f"Erro ao cadastrar: {e}"

def autenticar_usuario(username: str, senha: str) -> bool:
    with sqlite3.connect("sistema.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT salt, hash_senha FROM usuarios WHERE username = ?",
            (username.strip(),)
        )
        registro = cursor.fetchone()
        
        if not registro:
            return False
        
        salt, hash_gravado = registro
        _, hash_calculado = hash_senha(senha, salt)
        return hash_calculado == hash_gravado

# ----------------- INTERFACE GRÁFICA (TKINTER) ----------------- #

class SistemaLogin:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Acesso ao Sistema")
        self.root.geometry("380x340")
        self.root.resizable(False, False)
        
        self.container = tk.Frame(self.root, padx=24, pady=24)
        self.container.pack(fill="both", expand=True)

        self.carregar_tela_login()

    def limpar_tela(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def carregar_tela_login(self):
        self.limpar_tela()

        tk.Label(self.container, text="Login", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        tk.Label(self.container, text="Usuário:", anchor="w").pack(fill="x")
        self.entry_user = tk.Entry(self.container, font=("Arial", 11))
        self.entry_user.pack(fill="x", pady=(0, 10))

        tk.Label(self.container, text="Senha:", anchor="w").pack(fill="x")
        self.entry_pass = tk.Entry(self.container, show="*", font=("Arial", 11))
        self.entry_pass.pack(fill="x", pady=(0, 16))

        btn_entrar = tk.Button(
            self.container, text="Entrar", bg="#1976D2", fg="white",
            font=("Arial", 10, "bold"), relief="flat", pady=4,
            command=self.acao_login
        )
        btn_entrar.pack(fill="x", pady=(0, 8))

        btn_ir_cadastro = tk.Button(
            self.container, text="Não tem conta? Cadastre-se",
            relief="flat", fg="#555",
            command=self.carregar_tela_cadastro
        )
        btn_ir_cadastro.pack()

    def carregar_tela_cadastro(self):
        self.limpar_tela()

        tk.Label(self.container, text="Criar Conta", font=("Arial", 16, "bold")).pack(pady=(0, 16))

        tk.Label(self.container, text="Novo Usuário:", anchor="w").pack(fill="x")
        self.entry_novo_user = tk.Entry(self.container, font=("Arial", 11))
        self.entry_novo_user.pack(fill="x", pady=(0, 8))

        tk.Label(self.container, text="Senha:", anchor="w").pack(fill="x")
        self.entry_nova_pass = tk.Entry(self.container, show="*", font=("Arial", 11))
        self.entry_nova_pass.pack(fill="x", pady=(0, 8))

        tk.Label(self.container, text="Confirmar Senha:", anchor="w").pack(fill="x")
        self.entry_confirma_pass = tk.Entry(self.container, show="*", font=("Arial", 11))
        self.entry_confirma_pass.pack(fill="x", pady=(0, 14))

        btn_salvar = tk.Button(
            self.container, text="Cadastrar", bg="#388E3C", fg="white",
            font=("Arial", 10, "bold"), relief="flat", pady=4,
            command=self.acao_cadastrar
        )
        btn_salvar.pack(fill="x", pady=(0, 8))

        btn_voltar = tk.Button(
            self.container, text="Voltar para o Login",
            relief="flat", fg="#555",
            command=self.carregar_tela_login
        )
        btn_voltar.pack()

    def acao_login(self):
        user = self.entry_user.get()
        senha = self.entry_pass.get()

        if autenticar_usuario(user, senha):
            messagebox.showinfo("Sucesso", f"Bem-vindo(a), {user}!")
            self.entry_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")

    def acao_cadastrar(self):
        user = self.entry_novo_user.get()
        senha = self.entry_nova_pass.get()
        confirma = self.entry_confirma_pass.get()

        if senha != confirma:
            messagebox.showwarning("Aviso", "As senhas não coincidem.")
            return

        sucesso, msg = cadastrar_usuario(user, senha)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.carregar_tela_login()
        else:
            messagebox.showerror("Atenção", msg)

# ----------------- EXECUÇÃO ----------------- #

if __name__ == "__main__":
    init_db()
    app_root = tk.Tk()
    app = SistemaLogin(app_root)
    app_root.mainloop()
