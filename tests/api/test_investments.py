import csv
from pathlib import Path

import pytest
import requests


# Parte do integrante 3: criação de investimentos válidos (POST /api/investments).

CAMPOS_RESPOSTA_INVESTIMENTO = {
    "id", "user_id", "asset_name", "asset_type", "amount",
    "purchase_price", "days_invested", "planned_days", "annual_rate",
    "current_value", "future_value", "projected_profit",
}


@pytest.fixture
def investimentos_criados(base_url, auth_headers):
    """Guarda os IDs criados no teste e os exclui ao final (limpeza da massa)."""
    ids = []
    yield ids
    for investimento_id in ids:
        requests.delete(
            f"{base_url}/api/investments/{investimento_id}",
            headers=auth_headers,
            timeout=30,
        )
    print(f"[TEST_INVESTMENTS] Limpeza: {len(ids)} investimento(s) removido(s).")


def valor_em_reais_para_float(texto):
    """Converte um valor monetário da API (ex.: 'R$ 2.654,25') para float."""
    return float(texto.replace("R$", "").strip().replace(".", "").replace(",", "."))


def criar_investimento(base_url, auth_headers, payload):
    """Envia o POST de criação de investimento e retorna a resposta."""
    return requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers,
        timeout=30,
    )


@pytest.mark.parametrize("asset_name", ["CDB", "Poupança"])
def test_criar_investimento_valido(
    base_url, auth_headers, investimentos_criados, asset_name
):
    """Valida a criação de um investimento válido e o conteúdo da resposta (HTTP 201)."""
    payload = {
        "asset_name": asset_name,
        "amount": 2500.00,
        "purchase_price": 1.00,
        "days_invested": 90,
        "planned_days": 365,
    }
    print(f"\n[TEST_INVESTMENTS] Criando investimento em '{asset_name}'...")

    response = criar_investimento(base_url, auth_headers, payload)

    print(f"[TEST_INVESTMENTS] Status: {response.status_code}")
    print(f"[TEST_INVESTMENTS] Resposta: {response.text}")
    assert response.status_code == 201, (
        f"Esperado HTTP 201, recebido {response.status_code}: {response.text}"
    )

    dados = response.json()
    investimentos_criados.append(dados["id"])

    campos_faltando = CAMPOS_RESPOSTA_INVESTIMENTO - dados.keys()
    assert not campos_faltando, f"Campos ausentes na resposta: {campos_faltando}"

    assert isinstance(dados["id"], int)
    assert dados["asset_name"] == asset_name
    assert dados["amount"] == payload["amount"]
    assert dados["purchase_price"] == payload["purchase_price"]
    assert dados["days_invested"] == payload["days_invested"]
    assert dados["planned_days"] == payload["planned_days"]
    assert dados["annual_rate"] > 0, "A taxa anual do ativo deveria ser positiva."
    valor_atual = valor_em_reais_para_float(dados["current_value"])
    valor_futuro = valor_em_reais_para_float(dados["future_value"])
    assert valor_atual > 0, "O valor atual do investimento deveria ser positivo."
    assert valor_futuro >= valor_atual, (
        "O valor futuro não pode ser menor que o valor atual."
    )
    print(f"[TEST_INVESTMENTS] Investimento {dados['id']} criado com sucesso!")


def test_investimento_criado_aparece_na_listagem(
    base_url, auth_headers, investimentos_criados
):
    """Valida que o investimento criado passa a constar na carteira do usuário."""
    payload = {
        "asset_name": "CDB",
        "amount": 1500.00,
        "purchase_price": 1.00,
        "days_invested": 60,
        "planned_days": 720,
    }
    print("\n[TEST_INVESTMENTS] Criando investimento e conferindo a listagem...")

    criacao = criar_investimento(base_url, auth_headers, payload)
    assert criacao.status_code == 201, f"Erro ao criar: {criacao.text}"
    novo_id = criacao.json()["id"]
    investimentos_criados.append(novo_id)

    listagem = requests.get(
        f"{base_url}/api/investments", headers=auth_headers, timeout=30
    )
    assert listagem.status_code == 200

    encontrados = [item for item in listagem.json() if item["id"] == novo_id]
    assert len(encontrados) == 1, (
        f"O investimento {novo_id} não foi encontrado na listagem."
    )
    assert encontrados[0]["amount"] == payload["amount"]
    print(f"[TEST_INVESTMENTS] Investimento {novo_id} encontrado na listagem!")


def test_listar_investimentos(base_url, auth_headers):
    """Valida a listagem de investimentos do usuário autenticado."""

    print("\n[TEST_INVESTMENTS] Consultando investimentos...")

    response = requests.get(
        f"{base_url}/api/investments",
        headers=auth_headers
    )

    print("Status HTTP:", response.status_code)

    assert response.status_code == 200, (
        f"Erro ao listar investimentos: {response.text}"
    )

    investimentos = response.json()

    assert isinstance(investimentos, list), (
        "A resposta deveria ser uma lista."
    )

    print(
        f"[TEST_INVESTMENTS] Sucesso! "
        f"{len(investimentos)} investimentos encontrados."
    )


def test_excluir_investimento(base_url, auth_headers):
    """Valida a exclusão de um investimento."""

    print("\n[TEST_INVESTMENTS] Iniciando teste de exclusão...")

    # 1. Criar um investimento para o teste
    payload = {
        "asset_name": "CDB",
        "amount": 1000.00,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365
    }

    criacao = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers
    )

    print("Status da criação:", criacao.status_code)
    print("Resposta:", criacao.text)

    assert criacao.status_code == 201, (
        f"Erro ao criar investimento: {criacao.text}"
    )

    # 2. Recuperar o identificador
    dados = criacao.json()

    investimento_id = dados.get("investment_id") or dados.get("id")

    assert investimento_id is not None, (
        f"ID não encontrado na resposta: {dados}"
    )

    # 3. Excluir o investimento
    exclusao = requests.delete(
        f"{base_url}/api/investments/{investimento_id}",
        headers=auth_headers
    )

    print("Status da exclusão:", exclusao.status_code)
    print("Resposta:", exclusao.text)

    assert exclusao.status_code == 200, (
        f"Erro ao excluir investimento: {exclusao.text}"
    )

    # 4. Consultar novamente os investimentos
    listagem = requests.get(
        f"{base_url}/api/investments",
        headers=auth_headers
    )

    assert listagem.status_code == 200

    investimentos = listagem.json()

    # 5. Verificar se o investimento foi removido
    assert all(
        item.get("investment_id", item.get("id")) != investimento_id
        for item in investimentos
    ), "O investimento ainda aparece na listagem!"

    print("[TEST_INVESTMENTS] Investimento excluído com sucesso!")


# Parte do integrante 7: criação de investimentos com dados de um CSV.


def carregar_dados_investimentos_csv():
    """Localiza e lê a massa de testes independentemente da pasta de execução."""
    caminho_csv = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "dados_investimentos.csv"
    )
    if not caminho_csv.is_file():
        raise FileNotFoundError(
            f"Arquivo de massa CSV não encontrado em: {caminho_csv}"
        )

    casos = []
    with caminho_csv.open(mode="r", encoding="utf-8-sig", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            casos.append(
                (
                    linha["asset_name"],
                    float(linha["amount"]),
                    float(linha["purchase_price"]),
                    int(linha["days_invested"]),
                    int(linha["planned_days"]),
                    int(linha["status_esperado"]),
                )
            )
    if not casos:
        raise ValueError(f"O arquivo CSV não contém cenários: {caminho_csv}")
    return casos


@pytest.mark.parametrize(
    "asset, amount, price, days, planned, status_esperado",
    carregar_dados_investimentos_csv(),
)
def test_criar_investimentos_ddt_csv(
    base_url, auth_headers, asset, amount, price, days, planned,
    status_esperado,
):
    """Envia uma criação por linha e compara o status com o esperado no CSV."""
    payload = {
        "asset_name": asset,
        "amount": amount,
        "purchase_price": price,
        "days_invested": days,
        "planned_days": planned,
    }
    response = requests.post(
        f"{base_url.rstrip('/')}/api/investments",
        json=payload,
        headers=auth_headers,
        timeout=30,
    )
    assert response.status_code == status_esperado, (
        f"Ativo={asset}, valor={amount}: esperado HTTP {status_esperado}, "
        f"recebido HTTP {response.status_code}. Resposta: {response.text}"
    )
