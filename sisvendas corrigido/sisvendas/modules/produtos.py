import sqlite3
from typing import Optional, Dict, Any, List
from database.connection import get_connection


def formatar_codigo_barras(codigo: Optional[str]) -> Optional[str]:
    """Limpa e formata o código de barras, retornando None se vazio."""
    if codigo is None:
        return None
    codigo_limpo = str(codigo).strip()
    return codigo_limpo if codigo_limpo else None


def validar_dados_produto(
    nome: str,
    preco_custo: float,
    preco_venda: float,
    estoque: int
):
    """Valida as regras de negócio de um produto."""
    if not nome or not str(nome).strip():
        return False, "O nome do produto é obrigatório."

    if len(str(nome).strip()) < 2:
        return False, "O nome do produto deve ter pelo menos 2 caracteres."

    try:
        custo = float(preco_custo)
        if custo < 0:
            return False, "O preço de custo não pode ser negativo."
    except (ValueError, TypeError):
        return False, "Preço de custo inválido."

    try:
        venda = float(preco_venda)
        if venda < 0:
            return False, "O preço de venda não pode ser negativo."
    except (ValueError, TypeError):
        return False, "Preço de venda inválido."

    try:
        qtd_estoque = int(estoque)
        if qtd_estoque < 0:
            return False, "A quantidade em estoque não pode ser negativa."
    except (ValueError, TypeError):
        return False, "Quantidade de estoque inválida."

    return True, ""


def cadastrar_produto(
    nome: str,
    codigo_barras: Optional[str],
    preco_custo: float,
    preco_venda: float,
    estoque: int,
    ativo: int = 1
):
    """
    Cadastra um novo produto na tabela 'produtos'.
    Retorna (True, mensagem, produto_id) ou (False, mensagem_erro, None).
    """
    valido, msg_erro = validar_dados_produto(nome, preco_custo, preco_venda, estoque)
    if not valido:
        return False, msg_erro, None

    codigo_limpo = formatar_codigo_barras(codigo_barras)
    nome_limpo = str(nome).strip()
    custo = round(float(preco_custo), 2)
    venda = round(float(preco_venda), 2)
    qtd_estoque = int(estoque)
    status_ativo = 1 if ativo else 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if codigo_limpo is not None:
            cursor.execute("SELECT id FROM produtos WHERE codigo_barras = ?;", (codigo_limpo,))
            if cursor.fetchone():
                return False, f"O código de barras '{codigo_limpo}' já está em uso por outro produto.", None

        cursor.execute(
            """
            INSERT INTO produtos (nome, codigo_barras, preco_custo, preco_venda, estoque, ativo)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (nome_limpo, codigo_limpo, custo, venda, qtd_estoque, status_ativo)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return True, "Produto cadastrado com sucesso!", novo_id
    except sqlite3.Error as e:
        return False, f"Erro ao salvar produto: {str(e)}", None
    finally:
        conn.close()


def atualizar_produto(
    produto_id: int,
    nome: str,
    codigo_barras: Optional[str],
    preco_custo: float,
    preco_venda: float,
    estoque: int,
    ativo: int = 1
):
    """
    Atualiza as informações de um produto existente.
    Retorna (True, mensagem) ou (False, mensagem_erro).
    """
    valido, msg_erro = validar_dados_produto(nome, preco_custo, preco_venda, estoque)
    if not valido:
        return False, msg_erro

    codigo_limpo = formatar_codigo_barras(codigo_barras)
    nome_limpo = str(nome).strip()
    custo = round(float(preco_custo), 2)
    venda = round(float(preco_venda), 2)
    qtd_estoque = int(estoque)
    status_ativo = 1 if ativo else 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verifica se o produto existe
        cursor.execute("SELECT id FROM produtos WHERE id = ?;", (produto_id,))
        if not cursor.fetchone():
            return False, "Produto não encontrado."

        # Se houver código de barras, garante unicidade para outros registros
        if codigo_limpo is not None:
            cursor.execute(
                "SELECT id FROM produtos WHERE codigo_barras = ? AND id != ?;",
                (codigo_limpo, produto_id)
            )
            if cursor.fetchone():
                return False, f"O código de barras '{codigo_limpo}' já pertence a outro produto."

        cursor.execute(
            """
            UPDATE produtos
            SET nome = ?, codigo_barras = ?, preco_custo = ?, preco_venda = ?, estoque = ?, ativo = ?
            WHERE id = ?;
            """,
            (nome_limpo, codigo_limpo, custo, venda, qtd_estoque, status_ativo, produto_id)
        )
        conn.commit()
        return True, "Produto atualizado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao atualizar produto: {str(e)}"
    finally:
        conn.close()


def excluir_ou_desativar_produto(produto_id: int):
    """
    Exclui o produto se ele nunca participou de vendas.
    Se já participou de vendas, apenas desativa (soft delete) para preservar a integridade.
    Retorna (True, mensagem) ou (False, mensagem_erro).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Checa se o produto existe
        cursor.execute("SELECT nome FROM produtos WHERE id = ?;", (produto_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Produto não encontrado."
        nome_prod = row["nome"]

        # Checa se o produto está em itens_venda
        cursor.execute("SELECT COUNT(*) as total FROM itens_venda WHERE produto_id = ?;", (produto_id,))
        total_vendas = cursor.fetchone()["total"]

        if total_vendas > 0:
            # Não pode deletar fisicamente, desativa
            cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?;", (produto_id,))
            conn.commit()
            return True, f"O produto '{nome_prod}' já possui histórico de vendas e foi desativado."
        else:
            # Pode deletar fisicamente
            cursor.execute("DELETE FROM produtos WHERE id = ?;", (produto_id,))
            conn.commit()
            return True, f"Produto '{nome_prod}' excluído com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao processar exclusão: {str(e)}"
    finally:
        conn.close()


def obter_produto_por_id(produto_id: int) -> Optional[Dict[str, Any]]:
    """Busca um produto pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM produtos WHERE id = ?;", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def listar_produtos(termo_busca: str = "", apenas_ativos: bool = False) -> List[Dict[str, Any]]:
    """Lista os produtos cadastrados com opções de filtro por busca e status."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []

        if apenas_ativos:
            query += " AND ativo = 1"

        if termo_busca and termo_busca.strip():
            filtro = f"%{termo_busca.strip()}%"
            query += " AND (nome LIKE ? OR codigo_barras LIKE ?)"
            params.extend([filtro, filtro])

        query += " ORDER BY nome ASC;"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def metricas_produtos() -> Dict[str, Any]:
    """Calcula estatísticas rápidas dos produtos para o painel principal."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_produtos,
                SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) as total_ativos,
                SUM(CASE WHEN estoque = 0 AND ativo = 1 THEN 1 ELSE 0 END) as estoque_zerado,
                SUM(CASE WHEN estoque > 0 AND estoque <= 5 AND ativo = 1 THEN 1 ELSE 0 END) as estoque_baixo,
                SUM(estoque) as total_unidades,
                SUM(preco_custo * estoque) as valor_total_custo,
                SUM(preco_venda * estoque) as valor_total_venda
            FROM produtos;
        """)
        row = cursor.fetchone()
        return {
            "total_produtos": row["total_produtos"] or 0,
            "total_ativos": row["total_ativos"] or 0,
            "estoque_zerado": row["estoque_zerado"] or 0,
            "estoque_baixo": row["estoque_baixo"] or 0,
            "total_unidades": row["total_unidades"] or 0,
            "valor_total_custo": round(row["valor_total_custo"] or 0.0, 2),
            "valor_total_venda": round(row["valor_total_venda"] or 0.0, 2),
        }
    finally:
        conn.close()

