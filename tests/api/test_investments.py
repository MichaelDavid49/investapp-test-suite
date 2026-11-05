import csv
from pathlib import Path

import pytest
import requests


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
