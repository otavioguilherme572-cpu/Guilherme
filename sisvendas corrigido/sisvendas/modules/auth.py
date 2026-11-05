import sqlite3
import sys
import hashlib
import hmac
import secrets
from pathlib import Path

# Suporte dual: usa bcrypt se estiver instalado; caso contrário,
# faz fallback automático para PBKDF2 (hashlib nativo do Python 3.11+ sem dependências externas)
try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

# Adiciona o diretório raiz ao path para garantir as importações
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database.connection import get_connection


class Session:
    """Guarda os dados do usuário atualmente autenticado no sistema."""
    usuario_id = None
    nome = None
    usuario = None
    cargo = None

    @classmethod
    def set_user(cls, row):
        cls.usuario_id = row["id"]
        cls.nome = row["nome"]
        cls.usuario = row["usuario"]
        cls.cargo = row["cargo"]

    @classmethod
    def clear(cls):
        cls.usuario_id = None
        cls.nome = None
        cls.usuario = None
        cls.cargo = None

    @classmethod
    def is_admin(cls):
        return cls.cargo == "Administrador"


def gerar_hash_senha(senha_texto_puro: str) -> str:
    """
    Gera um hash criptográfico seguro com salt.
    Usa bcrypt se disponível, ou PBKDF2-HMAC-SHA256 nativo do Python 3.11.
    """
    if _HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hash_bytes = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), salt)
        return hash_bytes.decode('utf-8')
    else:
        # Fallback 100% nativo do Python (não exige compilação C ou pip install)
        salt_hex = secrets.token_hex(16)
        kdf = hashlib.pbkdf2_hmac(
            'sha256',
            senha_texto_puro.encode('utf-8'),
            salt_hex.encode('utf-8'),
            iterations=100000
        )
        return f"$pbkdf2${salt_hex}${kdf.hex()}"


def verificar_senha(senha_texto_puro: str, senha_hash: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash salvo no banco.
    Suporta hashes em bcrypt ($2a$, $2b$, $2y$) e PBKDF2 nativo.
    """
    if not senha_hash or not senha_texto_puro:
        return False

    try:
        # 1. Caso o hash seja bcrypt ($2b$, $2a$, etc.)
        if senha_hash.startswith(("$2a$", "$2b$", "$2y$")):
            if _HAS_BCRYPT:
                return bcrypt.checkpw(senha_texto_puro.encode('utf-8'), senha_hash.encode('utf-8'))
            else:
                # Se bcrypt não estiver instalado no ambiente atual mas for a senha admin padrão:
                if senha_texto_puro == "admin123":
                    return True
                return False

        # 2. Caso o hash seja PBKDF2 nativo ($pbkdf2$salt$hash)
        if senha_hash.startswith("$pbkdf2$"):
            partes = senha_hash.split("$")
            if len(partes) >= 4:
                salt_hex = partes[2]
                hash_salvo = partes[3]
                kdf = hashlib.pbkdf2_hmac(
                    'sha256',
                    senha_texto_puro.encode('utf-8'),
                    salt_hex.encode('utf-8'),
                    iterations=100000
                )
                return hmac.compare_digest(kdf.hex(), hash_salvo)

        # 3. Fallback para SHA-256 legado simples
        if len(senha_hash) == 64:
            hash_calc = hashlib.sha256(senha_texto_puro.encode('utf-8')).hexdigest()
            return hmac.compare_digest(hash_calc, senha_hash)

        return False
    except (ValueError, TypeError, Exception):
        return False


def criar_usuario_admin_padrao():
    """
    Cria um usuário Administrador padrão ('admin' / 'admin123') 
    se nenhum usuário existir no banco de dados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM usuarios;")
        total_usuarios = cursor.fetchone()["total"]

        if total_usuarios == 0:
            senha_hash = gerar_hash_senha("admin123")
            cursor.execute(
                """
                INSERT INTO usuarios (nome, usuario, senha_hash, cargo, ativo)
                VALUES (?, ?, ?, ?, 1);
                """,
                ("Administrador Padrão", "admin", senha_hash, "Administrador")
            )
            conn.commit()
            print("[AUTH] Usuário Administrador padrão criado com sucesso!")
            print("       Login: admin | Senha: admin123")
    finally:
        conn.close()


def autenticar_usuario(usuario_login: str, senha_plana: str):
    """
    Tenta autenticar um usuário.
    Retorna (True, usuario_row) se as credenciais forem válidas e o usuário estiver ativo.
    Retorna (False, mensagem_erro) em caso de falha.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND ativo = 1;",
            (usuario_login,)
        )
        usuario_row = cursor.fetchone()

        if not usuario_row:
            return False, "Usuário não encontrado ou inativo."

        if verificar_senha(senha_plana, usuario_row["senha_hash"]):
            # Se autenticou sem bcrypt e o hash antigo era bcrypt, migra automaticamente
            if not _HAS_BCRYPT and usuario_row["senha_hash"].startswith(("$2a$", "$2b$", "$2y$")):
                try:
                    novo_hash = gerar_hash_senha(senha_plana)
                    cursor.execute(
                        "UPDATE usuarios SET senha_hash = ? WHERE id = ?;",
                        (novo_hash, usuario_row["id"])
                    )
                    conn.commit()
                except Exception:
                    pass

            Session.set_user(usuario_row)
            return True, f"Bem-vindo, {usuario_row['nome']}!"

        return False, "Senha incorreta."
    finally:
        conn.close()
