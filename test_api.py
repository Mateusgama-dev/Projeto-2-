import pytest
from unittest.mock import patch, MagicMock
from api import app  # e.g., arquivo api.py com app = Flask(__name__)


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("api.conectar_banco")
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    """GET /contacts - lista vazia."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM tbl_imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_listar_imoveis_com_dados(mock_conectar_banco, client):
    """GET /imoveis - lista com dados."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, "x", "Conceição", "Osasco", "278383", "casa", "20000", "13/04/2002"),
        (2, "y", "Marina", "São Paulo", "374689", "AP", "3000000", "20/08/2009"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "x", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383","tipo":"casa", "valor":"20000", "data_aquisicao":"13/04/2002"},
        {"id": 2, "logradouro": "y", "bairro": "Marina", "cidade": "São Paulo", "cep":"374689","tipo":"AP", "valor":"3000000", "data_aquisicao":"20/08/2009"},
    ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM tbl_imoveis" 
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()