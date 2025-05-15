from . import BumpStikTestBase

class TestServerConnection(BumpStikTestBase):
    def test_successful_connection(self):
        """Testa conexão bem-sucedida ao servidor."""
        response = self.connect_to_server("localhost", 38281)
        self.assertEqual(response.status, "connected")

    def test_invalid_port(self):
        """Testa conexão com porta inválida."""
        response = self.connect_to_server("localhost", 12345)
        self.assertEqual(response.status, "error")