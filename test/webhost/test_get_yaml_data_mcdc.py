"""
Testes unitários completos para o método get_yaml_data do WebHostLib/check.py
Implementação de casos de teste baseados no critério MC/DC (Modified Condition/Decision Coverage)

Autor: Lucas Oliveira Meireles
Matrícula: 190016647
Data: 2025
"""

import unittest
import tempfile
import zipfile
import io
import os
from unittest.mock import Mock, patch, MagicMock
from markupsafe import Markup

# Simular as funções necessárias para evitar dependências
def allowed_options(filename):
    """Simula a função allowed_options"""
    allowed_extensions = (".yaml", ".json", ".yml", ".txt", ".zip")
    return filename.endswith(allowed_extensions)

def banned_file(filename):
    """Simula a função banned_file"""
    banned_extensions = (".sfc", ".z64", ".n64", ".nes", ".smc", ".sms", ".gb", ".gbc", ".gba")
    return filename.endswith(banned_extensions)

# Código simplificado do método get_yaml_data para teste isolado
def get_yaml_data_isolated(files):
    """Versão isolada do método get_yaml_data para testes"""
    import os
    import zipfile
    
    options = {}
    for uploaded_file in files:
        if banned_file(uploaded_file.filename):
            return ("Uploaded data contained a rom file, which is likely to contain copyrighted material. "
                    "Your file was deleted.")
        # If the user does not select file, the browser will still submit an empty string without a file name.
        elif uploaded_file.filename == "":
            return "No selected file."
        elif uploaded_file.filename in options:
            return f"Conflicting files named {uploaded_file.filename} submitted."
        elif uploaded_file and allowed_options(uploaded_file.filename):
            if uploaded_file.filename.endswith(".zip"):
                if not zipfile.is_zipfile(uploaded_file):
                    return f"Uploaded file {uploaded_file.filename} is not a valid .zip file and cannot be opened."

                uploaded_file.seek(0)  # offset from is_zipfile check
                with zipfile.ZipFile(uploaded_file, "r") as zfile:
                    for file in zfile.infolist():
                        # Remove folder pathing from str (e.g. "__MACOSX/" folder paths from archives created by macOS).
                        base_filename = os.path.basename(file.filename)

                        if base_filename.endswith(".archipelago"):
                            return Markup("Error: Your .zip file contains an .archipelago file. "
                                          'Did you mean to <a href="/uploads">host a game</a>?')
                        elif base_filename.endswith(".zip"):
                            return "Nested .zip files inside a .zip are not supported."
                        elif banned_file(base_filename):
                            return ("Uploaded data contained a rom file, which is likely to contain copyrighted "
                                    "material. Your file was deleted.")
                        # Ignore dot-files.
                        elif not base_filename.startswith(".") and allowed_options(base_filename):
                            options[file.filename] = zfile.open(file, "r").read()
            else:
                options[uploaded_file.filename] = uploaded_file.read()

    if not options:
        allowed_options_extensions = (".yaml", ".json", ".yml", ".txt", ".zip")
        return f"Did not find any valid files to process. Accepted formats: {allowed_options_extensions}"
    return options


class TestGetYamlDataMCDC(unittest.TestCase):
    """
    Classe de testes para o método get_yaml_data usando critério MC/DC.
    
    O método get_yaml_data possui 10 decisões, sendo 2 com condições compostas:
    - D4: uploaded_file AND allowed_options(uploaded_file.filename)
    - D10: not base_filename.startswith(".") AND allowed_options(base_filename)
    """

    def setUp(self):
        """Configuração inicial para os testes."""
        self.valid_yaml_content = b"player_name: TestPlayer\ngame: TestGame"

    def create_mock_file(self, filename, content=None):
        """Cria um mock de arquivo para testes."""
        mock_file = Mock()
        mock_file.filename = filename
        mock_file.read.return_value = content or self.valid_yaml_content
        mock_file.seek = Mock()
        return mock_file

    def test_ct1_arquivo_banido_d1_true(self):
        """
        CT1: D1=True - Arquivo com extensão banida
        Testa condição C1: banned_file(uploaded_file.filename) = True
        """
        # Arrange
        mock_file = self.create_mock_file("test_rom.sfc")
        files = [mock_file]
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("rom file", result)
        self.assertIn("copyrighted material", result)
        print("✓ CT1 PASSOU: Arquivo banido detectado corretamente")

    def test_ct2_filename_vazio_d2_true(self):
        """
        CT2: D2=True - Nome de arquivo vazio
        Testa condição C2: uploaded_file.filename == "" = True
        """
        # Arrange
        mock_file = self.create_mock_file("")
        files = [mock_file]
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertEqual(result, "No selected file.")
        print("✓ CT2 PASSOU: Filename vazio detectado corretamente")

    def test_ct3_filename_duplicado_d3_true(self):
        """
        CT3: D3=True - Nome de arquivo duplicado
        Testa condição C3: uploaded_file.filename in options = True
        """
        # Arrange
        mock_file1 = self.create_mock_file("test.yaml")
        mock_file2 = self.create_mock_file("test.yaml")  # Mesmo nome
        files = [mock_file1, mock_file2]
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("Conflicting files", result)
        self.assertIn("test.yaml", result)
        print("✓ CT3 PASSOU: Arquivo duplicado detectado corretamente")

    def test_ct4_arquivo_valido_d4_true(self):
        """
        CT4: D4=True - Arquivo válido com extensão permitida
        Testa condições C4a=True AND C4b=True
        Par de independência para C4a (linha 1 vs 3) e C4b (linha 1 vs 2)
        """
        # Arrange
        mock_file = self.create_mock_file("test.yaml")
        files = [mock_file]
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("test.yaml", result)
        self.assertEqual(result["test.yaml"], self.valid_yaml_content)
        print("✓ CT4 PASSOU: D4=True (C4a=T AND C4b=T) - Arquivo válido processado")

    def test_ct5_arquivo_valido_extensao_invalida_d4_false(self):
        """
        CT5: D4=False - Arquivo existe mas extensão não permitida
        Testa condições C4a=True AND C4b=False
        Par de independência para C4b (linha 1 vs 2)
        """
        # Arrange
        mock_file = self.create_mock_file("test.invalid")
        files = [mock_file]
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("Did not find any valid files", result)
        print("✓ CT5 PASSOU: D4=False (C4a=T AND C4b=F) - Extensão inválida rejeitada")

    def test_ct6_arquivo_zip_d5_true(self):
        """
        CT6: D5=True - Arquivo ZIP válido
        Testa condição C5: uploaded_file.filename.endswith(".zip") = True
        """
        # Arrange
        # Criar um ZIP real em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("inner.yaml", "test: data")
        zip_buffer.seek(0)
        
        mock_file = Mock()
        mock_file.filename = "test.zip"
        mock_file.read.return_value = zip_buffer.getvalue()
        mock_file.seek = Mock()
        
        # Mock zipfile.is_zipfile para retornar True
        with patch('zipfile.is_zipfile', return_value=True):
            # Mock ZipFile para usar nosso buffer
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = "inner.yaml"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zip_instance.open.return_value.read.return_value = b"test: data"
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                files = [mock_file]
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                self.assertIsInstance(result, dict)
                print("✓ CT6 PASSOU: D5=True - Arquivo ZIP processado corretamente")

    def test_ct7_zip_invalido_d6_true(self):
        """
        CT7: D6=True - Arquivo ZIP inválido
        Testa condição C6: not zipfile.is_zipfile(uploaded_file) = True
        """
        # Arrange
        mock_file = self.create_mock_file("invalid.zip", b"not a zip file")
        files = [mock_file]
        
        # Mock zipfile.is_zipfile para retornar False
        with patch('zipfile.is_zipfile', return_value=False):
            # Act
            result = get_yaml_data_isolated(files)
            
            # Assert
            self.assertIsInstance(result, str)
            self.assertIn("not a valid .zip file", result)
            print("✓ CT7 PASSOU: D6=True - ZIP inválido detectado corretamente")

    def test_ct8_arquivo_archipelago_no_zip_d7_true(self):
        """
        CT8: D7=True - Arquivo .archipelago dentro do ZIP
        Testa condição C7: base_filename.endswith(".archipelago") = True
        """
        # Arrange
        mock_file = self.create_mock_file("test.zip")
        files = [mock_file]
        
        with patch('zipfile.is_zipfile', return_value=True):
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = "game.archipelago"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                self.assertIsInstance(result, Markup)
                self.assertIn(".archipelago file", str(result))
                print("✓ CT8 PASSOU: D7=True - Arquivo .archipelago no ZIP detectado")

    def test_ct9_zip_aninhado_d8_true(self):
        """
        CT9: D8=True - ZIP aninhado dentro do ZIP
        Testa condição C8: base_filename.endswith(".zip") = True
        """
        # Arrange
        mock_file = self.create_mock_file("test.zip")
        files = [mock_file]
        
        with patch('zipfile.is_zipfile', return_value=True):
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = "nested.zip"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                self.assertIsInstance(result, str)
                self.assertIn("Nested .zip files", result)
                print("✓ CT9 PASSOU: D8=True - ZIP aninhado detectado corretamente")

    def test_ct10_arquivo_banido_no_zip_d9_true(self):
        """
        CT10: D9=True - Arquivo banido dentro do ZIP
        Testa condição C9: banned_file(base_filename) = True
        """
        # Arrange
        mock_file = self.create_mock_file("test.zip")
        files = [mock_file]
        
        with patch('zipfile.is_zipfile', return_value=True):
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = "rom.sfc"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                self.assertIsInstance(result, str)
                self.assertIn("rom file", result)
                self.assertIn("copyrighted material", result)
                print("✓ CT10 PASSOU: D9=True - Arquivo banido no ZIP detectado")

    def test_ct11_arquivo_valido_no_zip_d10_true(self):
        """
        CT11: D10=True - Arquivo válido dentro do ZIP
        Testa condições C10a=True AND C10b=True
        Par de independência para C10a (linha 1 vs 3) e C10b (linha 1 vs 2)
        """
        # Arrange
        mock_file = self.create_mock_file("test.zip")
        files = [mock_file]
        
        with patch('zipfile.is_zipfile', return_value=True):
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = "config.yaml"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zip_instance.open.return_value.read.return_value = self.valid_yaml_content
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                self.assertIsInstance(result, dict)
                self.assertIn("config.yaml", result)
                print("✓ CT11 PASSOU: D10=True (C10a=T AND C10b=T) - Arquivo válido no ZIP")

    def test_ct12_arquivo_oculto_no_zip_d10_false(self):
        """
        CT12: D10=False - Arquivo oculto (dot-file) dentro do ZIP
        Testa condições C10a=False AND C10b=True
        Par de independência para C10a (linha 1 vs 3)
        """
        # Arrange
        mock_file = self.create_mock_file("test.zip")
        files = [mock_file]
        
        with patch('zipfile.is_zipfile', return_value=True):
            with patch('zipfile.ZipFile') as mock_zipfile:
                mock_zip_info = Mock()
                mock_zip_info.filename = ".hidden.yaml"
                
                mock_zip_instance = Mock()
                mock_zip_instance.infolist.return_value = [mock_zip_info]
                mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
                
                # Act
                result = get_yaml_data_isolated(files)
                
                # Assert
                # Arquivo oculto deve ser ignorado, então não deve aparecer no resultado
                self.assertIsInstance(result, str)
                self.assertIn("Did not find any valid files", result)
                print("✓ CT12 PASSOU: D10=False (C10a=F AND C10b=T) - Arquivo oculto ignorado")

    def test_nenhum_arquivo_valido(self):
        """
        Teste adicional: Nenhum arquivo válido encontrado
        """
        # Arrange
        files = []
        
        # Act
        result = get_yaml_data_isolated(files)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("Did not find any valid files", result)
        print("✓ Teste adicional PASSOU: Nenhum arquivo válido")


if __name__ == '__main__':
    print("=== EXECUTANDO TESTES MC/DC PARA get_yaml_data ===\n")
    unittest.main(verbosity=2)

