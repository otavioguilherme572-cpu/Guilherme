import sqlite3
import re
from database.connection import get_connection
from modules.auth import gerar_hash_senha


def validar_dados_usuario(nome: str, usuario: str, senha: str, cargo: str):
    """Valida as regras de negócio para cadastro de usuário."""
    if not nome or not nome.strip():
        return False, "O nome completo é obrigatório."

    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False, "O nome deve conter pelo menos 3 caracteres."

    if not usuario or not usuario.strip():
        return False, "O nome de usuário (login) é obrigatório."

    usuario_limpo = usuario.strip().lower()
    if len(usuario_limpo) < 3:
        return False, "O nome de usuário deve conter pelo menos 3 caracteres."

    if not re.match(r"^[a-zA-Z0-9_.-]+$", usuario_limpo):
        return False, "O nome de usuário deve conter apenas letras, números, ponto ou traço."

    if not senha or len(senha) < 4:
        return False, "A senha deve conter pelo menos 4 caracteres."

    if cargo not in ("Administrador", "Vendedor"):
        return False, "O cargo deve ser 'Administrador' ou 'Vendedor'."

    return True, ""


def cadastrar_usuario(nome: str, usuario: str, senha: str, cargo: str, ativo: int = 1):
    """
    Cadastra um novo usuário no sistema.
    Retorna (True, mensagem) em caso de sucesso ou (False, mensagem_erro) em caso de falha.
    """
    valido, msg_erro = validar_dados_usuario(nome, usuario, senha, cargo)
    if not valido:
        return False, msg_erro

    nome_limpo = nome.strip()
    usuario_limpo = usuario.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE LOWER(usuario) = ?;", (usuario_limpo,))
        if cursor.fetchone():
            return False, f"O nome de usuário '{usuario_limpo}' já está em uso."

        senha_hash = gerar_hash_senha(senha)
        cursor.execute(
            """
            INSERT INTO usuarios (nome, usuario, senha_hash, cargo, ativo)
            VALUES (?, ?, ?, ?, ?);
            """,
            (nome_limpo, usuario_limpo, senha_hash, cargo, int(ativo))
        )
        conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao acessar o banco de dados: {str(e)}"
    finally:
        conn.close()


def listar_usuarios(termo_busca: str = ""):
    """Retorna uma lista de usuários cadastrados com filtro opcional."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if termo_busca and termo_busca.strip():
            filtro = f"%{termo_busca.strip()}%"
            cursor.execute(
                """
                SELECT id, nome, usuario, cargo, ativo, criado_em 
                FROM usuarios 
                WHERE nome LIKE ? OR usuario LIKE ?
                ORDER BY nome ASC;
                """,
                (filtro, filtro)
            )
        else:
            cursor.execute(
                """
                SELECT id, nome, usuario, cargo, ativo, criado_em 
                FROM usuarios 
                ORDER BY nome ASC;
                """
            )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def atualizar_status_usuario(usuario_id: int, ativo: int):
    """Ativa ou desativa um usuário no sistema."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE usuarios SET ativo = ? WHERE id = ?;",
            (1 if ativo else 0, usuario_id)
        )
        conn.commit()
        return True, "Status do usuário atualizado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao atualizar status: {str(e)}"
    finally:
        conn.close()


def contar_usuarios():
    """Retorna o total de usuários cadastrados e o total de ativos."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) as total, SUM(ativo) as ativos FROM usuarios;")
        row = cursor.fetchone()
        total = row["total"] if row and row["total"] else 0
        ativos = row["ativos"] if row and row["ativos"] else 0
        return {"total": total, "ativos": ativos}
    finally:
        conn.close()

