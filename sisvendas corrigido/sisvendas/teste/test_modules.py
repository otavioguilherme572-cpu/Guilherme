import unittest
import sys
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database.connection import init_db, get_connection
from modules.auth import criar_usuario_admin_padrao, autenticar_usuario
from modules.usuarios import cadastrar_usuario, listar_usuarios, contar_usuarios
from modules.produtos import (
    cadastrar_produto,
    atualizar_produto,
    listar_produtos,
    obter_produto_por_id,
    excluir_ou_desativar_produto,
    metricas_produtos
)


class TestModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        criar_usuario_admin_padrao()
        cls._limpar_dados_teste()

    @classmethod
    def tearDownClass(cls):
        cls._limpar_dados_teste()

    @classmethod
    def _limpar_dados_teste(cls):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM usuarios WHERE usuario LIKE 'test_%';")
        c.execute("DELETE FROM produtos WHERE nome LIKE 'Teste Prod%';")
        conn.commit()
        conn.close()

    def test_01_cadastro_usuario(self):
        login_teste = f"test_user_{uuid.uuid4().hex[:6]}"
        # Usuário válido
        sucesso, msg = cadastrar_usuario("Vendedor Silva", login_teste, "senha123", "Vendedor")
        self.assertTrue(sucesso)

        # Não deve permitir usuário duplicado
        sucesso_dup, msg_dup = cadastrar_usuario("Outro", login_teste, "senha123", "Vendedor")
        self.assertFalse(sucesso_dup)

        # Autenticação com novo usuário
        auth_ok, _ = autenticar_usuario(login_teste, "senha123")
        self.assertTrue(auth_ok)

    def test_02_produtos_crud(self):
        cb_teste = f"789{uuid.uuid4().int % 1000000000:09d}"
        nome_teste = f"Teste Prod {uuid.uuid4().hex[:4]}"

        # Cadastro de produto
        sucesso, msg, prod_id = cadastrar_produto(
            nome=nome_teste,
            codigo_barras=cb_teste,
            preco_custo=6.50,
            preco_venda=10.00,
            estoque=50
        )
        self.assertTrue(sucesso)
        self.assertIsNotNone(prod_id)

        # Busca por código ou nome
        prods = listar_produtos(nome_teste)
        self.assertTrue(len(prods) >= 1)
        self.assertEqual(prods[0]["nome"], nome_teste)

        # Atualização de produto
        sucesso_up, msg_up = atualizar_produto(
            produto_id=prod_id,
            nome=f"{nome_teste} Editado",
            codigo_barras=cb_teste,
            preco_custo=6.50,
            preco_venda=11.00,
            estoque=45,
            ativo=1
        )
        self.assertTrue(sucesso_up)

        prod_atualizado = obter_produto_por_id(prod_id)
        self.assertEqual(prod_atualizado["nome"], f"{nome_teste} Editado")
        self.assertEqual(prod_atualizado["preco_venda"], 11.00)

        # Métricas
        metricas = metricas_produtos()
        self.assertGreaterEqual(metricas["total_produtos"], 1)

        # Exclusão (sem vendas registradas)
        sucesso_del, msg_del = excluir_ou_desativar_produto(prod_id)
        self.assertTrue(sucesso_del)


if __name__ == "__main__":
    unittest.main()
