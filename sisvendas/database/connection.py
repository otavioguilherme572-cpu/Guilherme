import sqlite3
from pathlib import Path

# Garante caminhos absolutos baseados na localização do arquivo connection.py
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "sistema_vendas.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection():
    """Conecta ao SQLite e ativa suporte a Chaves Estrangeiras (Foreign Keys)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome: row['nome']
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Cria as tabelas do banco conforme o schema do sistema."""
    conn = get_connection()
    try:
        with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())
        conn.commit()
    finally:
        conn.close()

