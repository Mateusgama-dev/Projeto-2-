# Projeto 2 - API de Imóveis

API REST desenvolvida em Flask para gerenciamento de um cadastro de imóveis, com persistência em banco de dados MySQL. Permite listar, buscar, cadastrar, atualizar e remover registros de imóveis, com filtros por tipo e cidade.

## API em produção

> 🔗 **http://50.19.144.117/imoveis** _a preencher assim que o deploy for concluído_

## Funcionalidades

| Método | Rota                | Descrição                                                           |
|--------|---------------------|----------------------------------------------------------------------|
| GET    | `/imoveis`          | Lista todos os imóveis. Aceita filtros opcionais `?tipo=` e `?cidade=` |
| GET    | `/imoveis/<id>`     | Retorna um imóvel específico pelo `id`                               |
| POST   | `/imoveis`          | Cadastra um novo imóvel                                               |
| PUT    | `/imoveis/<id>`     | Atualiza um imóvel existente pelo `id`                                |
| DELETE | `/imoveis/<id>`     | Remove um imóvel pelo `id`                                            |

### Campos do imóvel

`logradouro`, `bairro`, `cidade`, `cep`, `tipo`, `valor`, `data_aquisicao`

## Tecnologias

- [Flask](https://flask.palletsprojects.com/) — framework web
- [MySQL](https://www.mysql.com/) — banco de dados relacional
- [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/) — driver de conexão com o MySQL
- [python-dotenv](https://pypi.org/project/python-dotenv/) — carregamento de variáveis de ambiente
- [pytest](https://docs.pytest.org/) — testes automatizados

## Estrutura do projeto

```
.
├── api.py                 # Rotas e regras da API
├── conexao.py              # Conexão com o banco MySQL
├── test_api_imoveis.py     # Testes automatizados (com mocks do banco)
├── certificados/
│   └── ca.pem               # Certificado de autoridade (CA) para conexão SSL com o MySQL
└── requirements.txt
```

## Configuração

A conexão com o banco é feita via variáveis de ambiente, carregadas de um arquivo `.env` na raiz do projeto (não versionado). Crie o arquivo com as seguintes chaves:

```
DB_HOST=<host do banco MySQL>
DB_PORT=<porta, ex: 3306>
DB_USER=<usuário>
DB_PASSWORD=<senha>
DB_NAME=<nome do banco>
DB_SSL_CA=certificados/ca.pem
```

O certificado `certificados/ca.pem` é usado para validar a conexão SSL com o banco.

## Como rodar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure o arquivo `.env` conforme a seção [Configuração](#configuração).
3. Suba o servidor:
   ```bash
   python api.py
   ```
   A API ficará disponível em `http://localhost:5000`.

## Testes

Os testes usam mocks para a conexão com o banco, não sendo necessário um MySQL disponível para rodá-los:

```bash
pytest test_api_imoveis.py
```
