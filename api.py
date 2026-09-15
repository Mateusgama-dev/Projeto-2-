from flask import Flask, request, jsonify
from conexao import conectar_banco

app = Flask(__name__)


CAMPOS_IMOVEL = [
    "logradouro",
    "tipo_logradouro",
    "bairro",
    "cidade",
    "cep",
    "tipo",
    "valor",
    "data_aquisicao",
]


def build_imovel_links(id):
    return [
        {"rel": "self", "href": f"/imoveis/{id}", "method": "GET"},
        {"rel": "update", "href": f"/imoveis/{id}", "method": "PUT"},
        {"rel": "delete", "href": f"/imoveis/{id}", "method": "DELETE"},
        {"rel": "collection", "href": "/imoveis", "method": "GET"},
    ]


def build_collection_links():
    return [
        {"rel": "self", "href": "/imoveis", "method": "GET"},
        {"rel": "create", "href": "/imoveis", "method": "POST"},
    ]


def row_to_imovel_dict(row):
    imovel_id = row[0]
    return {
        "id": imovel_id,
        "logradouro": row[1],
        "tipo_logradouro": row[2],
        "bairro": row[3],
        "cidade": row[4],
        "cep": row[5],
        "tipo": row[6],
        "valor": row[7],
        "data_aquisicao": row[8],
        "links": build_imovel_links(imovel_id),
    }


@app.route("/", methods=["GET"])
def index():
    """Ponto de entrada da API: lista os recursos e ações disponíveis (HATEOAS)."""
    return jsonify({"links": [{"rel": "self", "href": "/", "method": "GET"}] + build_collection_links()}), 200


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    """Lista todos os imóveis, com filtro opcional por tipo ou cidade (?tipo=... / ?cidade=...)."""
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")

    conn = conectar_banco()
    cursor = conn.cursor()

    if tipo:
        cursor.execute("SELECT * FROM imoveis WHERE tipo = %s", (tipo,))
    elif cidade:
        cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
    else:
        cursor.execute("SELECT * FROM imoveis")

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([row_to_imovel_dict(r) for r in rows]), 200


@app.route("/imoveis/<int:id>", methods=["GET"])
def obter_imovel(id):
    """Retorna um imóvel específico pelo id."""
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"erro": "Imóvel não encontrado"}), 404
    return jsonify(row_to_imovel_dict(row)), 200


@app.route("/imoveis", methods=["POST"])
def criar_imovel():
    """Cria um novo imóvel."""
    data = request.get_json(silent=True) or {}
    if not all(campo in data for campo in CAMPOS_IMOVEL):
        return jsonify({"erro": "Campos obrigatórios: " + ", ".join(CAMPOS_IMOVEL)}), 400

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        tuple(data[campo] for campo in CAMPOS_IMOVEL),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conn.close()

    response = jsonify({"id": novo_id, "links": build_imovel_links(novo_id)})
    response.status_code = 201
    response.headers["Location"] = f"/imoveis/{novo_id}"
    return response


@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):
    """Atualiza um imóvel existente."""
    data = request.get_json(silent=True) or {}
    if not all(campo in data for campo in CAMPOS_IMOVEL):
        return jsonify({"erro": "Campos obrigatórios: " + ", ".join(CAMPOS_IMOVEL)}), 400

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, "
        "cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        tuple(data[campo] for campo in CAMPOS_IMOVEL) + (id,),
    )
    conn.commit()
    encontrado = cursor.rowcount > 0
    cursor.close()
    conn.close()

    if not encontrado:
        return jsonify({"erro": "Imóvel não encontrado"}), 404
    return jsonify({"mensagem": "Imóvel atualizado com sucesso", "links": build_imovel_links(id)}), 200


@app.route("/imoveis/<int:id>", methods=["DELETE"])
def deletar_imovel(id):
    """Remove um imóvel pelo id."""
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM imoveis WHERE id = %s", (id,))
    conn.commit()
    encontrado = cursor.rowcount > 0
    cursor.close()
    conn.close()

    if not encontrado:
        return jsonify({"erro": "Imóvel não encontrado"}), 404
    return jsonify({"mensagem": "Imóvel excluído com sucesso", "links": build_collection_links()}), 200


if __name__ == "__main__":
    app.run(debug=True)
