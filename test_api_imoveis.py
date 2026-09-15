import pytest
from unittest.mock import patch, MagicMock
from api import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("api.conectar_banco")
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    """GET /imoveis - lista vazia."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")
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
        (1, "x", "Rua", "Conceição", "Osasco", "278383", "casa", "20000", "13/04/2002"),
        (2, "y", "Avenida", "Marina", "São Paulo", "374689", "AP", "3000000", "20/08/2009"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383", "tipo": "casa", "valor": "20000", "data_aquisicao": "13/04/2002"},
        {"id": 2, "logradouro": "y", "tipo_logradouro": "Avenida", "bairro": "Marina", "cidade": "São Paulo", "cep": "374689", "tipo": "AP", "valor": "3000000", "data_aquisicao": "20/08/2009"},
    ]

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_listar_imovel_com_dados(mock_conectar_banco, client):
    """GET /imoveis/<int:id> - imóvel existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "x", "Rua", "Conceição", "Osasco", "278383", "casa", "20000", "13/04/2002")

    response = client.get("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383", "tipo": "casa", "valor": "20000", "data_aquisicao": "13/04/2002"}

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis WHERE id = %s", (1,))
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_listar_imovel_invalido(mock_conectar_banco, client):
    """GET /imoveis/<int:id> - imóvel não existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    response = client.get("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@patch("api.conectar_banco")
def test_criar_imovel_ok(mock_conectar_banco, client):
    """POST /imoveis - cria imóvel com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.lastrowid = 10
    mock_conectar_banco.return_value = mock_conn

    payload = {"logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383", "tipo": "casa", "valor": "20000", "data_aquisicao": "13/04/2002"}
    response = client.post("/imoveis", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 10}

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        ("x", "Rua", "Conceição", "Osasco", "278383", "casa", "20000", "13/04/2002"),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    """POST /imoveis - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.post("/imoveis", json={"logradouro": "Rua Santos"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()


@patch("api.conectar_banco")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - deleta com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = %s", (1,))
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_deletar_imovel_not_found(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = %s", (999,))
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_atualizar_imoveis_ok(mock_conectar_banco, client):
    """PUT /imoveis/<id> - atualiza com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    payload = {"logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383", "tipo": "casa", "valor": "20000", "data_aquisicao": "13/04/2002"}
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("x", "Rua", "Conceição", "Osasco", "278383", "casa", "20000", "13/04/2002", 1),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    """PUT /imoveis/<id> - imovel não encontrado (rowcount=0)."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload = {"logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383","tipo":"casa", "valor":"20000", "data_aquisicao":"13/04/2002"}
    response = client.put("/imoveis/999", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("x", "Rua", "Conceição", "Osasco", "278383", "casa","20000", "13/04/2002", 999),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.conectar_banco")
def test_atualizar_imovel_erro_validacao(mock_conectar_banco, client):
    """PUT /imoveis/<id> - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.put("/imoveis/1", json={"logradouro": "Rua Silva"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()


@pytest.mark.parametrize("tipo", ["casa", "apartamento", "terreno"])
@patch("api.conectar_banco")
def test_buscar_imoveis_por_tipo(mock_conectar_banco, client, tipo):
    """GET /imoveis?tipo=<tipo> - retorna somente imóveis do tipo <tipo>."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, "x", "Rua", "Conceição", "Osasco", "278383", tipo, "20000", "13/04/2002"),
        (2, "y", "Avenida", "Marina", "São Paulo", "374689", tipo, "3000000", "20/08/2009"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get(f"/imoveis?tipo={tipo}")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": "Osasco", "cep": "278383", "tipo": tipo, "valor": "20000", "data_aquisicao": "13/04/2002"},
        {"id": 2, "logradouro": "y", "tipo_logradouro": "Avenida", "bairro": "Marina", "cidade": "São Paulo", "cep": "374689", "tipo": tipo, "valor": "3000000", "data_aquisicao": "20/08/2009"},
    ]

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis WHERE tipo = %s", (tipo,))
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@pytest.mark.parametrize("cidade", ["Osasco", "São Paulo", "Campinas"])
@patch("api.conectar_banco")
def test_buscar_imoveis_por_cidade(mock_conectar_banco, client, cidade):
    """GET /imoveis?cidade=<x> - retorna somente imóveis da cidade x."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, "x", "Rua", "Conceição", cidade, "278383", "casa", "20000", "13/04/2002"),
        (2, "y", "Avenida", "Marina", cidade, "374689", "casa", "3000000", "20/08/2009"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get(f"/imoveis?cidade={cidade}")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "x", "tipo_logradouro": "Rua", "bairro": "Conceição", "cidade": cidade, "cep": "278383", "tipo": "casa", "valor": "20000", "data_aquisicao": "13/04/2002"},
        {"id": 2, "logradouro": "y", "tipo_logradouro": "Avenida", "bairro": "Marina", "cidade": cidade, "cep": "374689", "tipo": "casa", "valor": "3000000", "data_aquisicao": "20/08/2009"},
    ]

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
