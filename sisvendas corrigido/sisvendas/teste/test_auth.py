import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database.connection import init_db
from modules.auth import (
    gerar_hash_senha, 
    verificar_senha, 
    criar_usuario_admin_padrao, 
    autenticar_usuario,
    Session
)

class TestAuthModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        criar_usuario_admin_padrao()

    def test_01_hash_senha(self):
        senha = "minhasenha123"
        hash_gerado = gerar_hash_senha(senha)
        self.assertTrue(verificar_senha(senha, hash_gerado))
        self.assertFalse(verificar_senha("senhaerrada", hash_gerado))

    def test_02_login_admin_padrao_sucesso(self):
        sucesso, msg = autenticar_usuario("admin", "admin123")
        self.assertTrue(sucesso)
        self.assertEqual(Session.usuario, "admin")
        self.assertTrue(Session.is_admin())

if __name__ == "__main__":
    unittest.main()