"""Parte do integrante 7: criação de investimentos com dados de um CSV."""

import csv
from pathlib import Path

import pytest
import requests


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
