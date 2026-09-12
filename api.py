from flask import Flask, request, jsonify
from conexao import conectar_banco

app = Flask(__name__)


CAMPOS_IMOVEL = ["logradouro", "bairro", "cidade", "cep", "tipo", "valor", "data_aquisicao"]


def row_to_imovel_dict(row):
    return {
        "id": row[0],
        "logradouro": row[1],
        "bairro": row[2],
        "cidade": row[3],
        "cep": row[4],
        "tipo": row[5],
        "valor": row[6],
        "data_aquisicao": row[7],
    }


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
        "INSERT INTO imoveis (logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        tuple(data[campo] for campo in CAMPOS_IMOVEL),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):
    """Atualiza um imóvel existente."""
    data = request.get_json(silent=True) or {}
    if not all(campo in data for campo in CAMPOS_IMOVEL):
        return jsonify({"erro": "Campos obrigatórios: " + ", ".join(CAMPOS_IMOVEL)}), 400

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imoveis SET logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, "
        "valor = %s, data_aquisicao = %s WHERE id = %s",
        tuple(data[campo] for campo in CAMPOS_IMOVEL) + (id,),
    )
    conn.commit()
    encontrado = cursor.rowcount > 0
    cursor.close()
    conn.close()

    if not encontrado:
        return jsonify({"erro": "Imóvel não encontrado"}), 404
    return jsonify({"mensagem": "Imóvel atualizado com sucesso"}), 200


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
    return jsonify({"mensagem": "Imóvel excluído com sucesso"}), 200


if __name__ == "__main__":
    app.run(debug=True)
