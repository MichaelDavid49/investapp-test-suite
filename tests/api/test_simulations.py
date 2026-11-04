
import os

import pytest
import requests


BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://5bm1nctd1f.execute-api.us-east-1.amazonaws.com",
).rstrip("/")

LOGIN_URL = f"{BASE_URL}/api/login"
SIMULATION_URL = f"{BASE_URL}/api/simulate/tax-withdrawal"


@pytest.fixture(scope="session")
def auth_headers():
    """Obtém autenticação usando credenciais ou token configurados localmente."""

    token = os.getenv("API_TOKEN")

    if token:
        return {"Authorization": f"Bearer {token}"}

    username = os.getenv("TEST_USER")
    password = os.getenv("TEST_PASSWORD")

    if not username or not password:
        pytest.skip(
            "Teste dependente de autenticação: "
            "configure API_TOKEN ou TEST_USER e TEST_PASSWORD."
        )

    response = requests.post(
        LOGIN_URL,
        data={
            "username": username,
            "password": password,
        },
        headers={"Accept": "application/json"},
        timeout=30,
    )

    assert response.status_code == 200, (
        f"Falha no login: HTTP {response.status_code}. "
        f"Resposta: {response.text}"
    )

    login_data = response.json()
    access_token = login_data.get("access_token")

    assert access_token, "A resposta de login não contém access_token."

    token_type = login_data.get("token_type", "bearer")

    return {
        "Authorization": f"{token_type} {access_token}"
    }


def test_simular_rendimento_mensal(base_url, auth_headers):
    """Valida a simulação de rendimento mensal da API."""

    payload = {
        "months": 12
    }

    response = requests.post(
        f"{base_url}/api/simulate/yield-monthly",
        json=payload,
        headers=auth_headers,
        timeout=30,
    )

    assert response.status_code == 200, (
        f"Esperado HTTP 200, recebido {response.status_code}: "
        f"{response.text}"
    )

    resultado = response.json()

    assert isinstance(resultado, dict), (
        "Formato inesperado: esperado objeto JSON (dict), "
        f"recebido {type(resultado).__name__}."
    )

    assert len(resultado) > 0


def test_tax_withdrawal_success(auth_headers):
    """Verifica uma simulação com target_amount numérico."""

    response = requests.post(
        SIMULATION_URL,
        json={"target_amount": 1000},
        headers={
            **auth_headers,
            "Accept": "application/json",
        },
        timeout=30,
    )

    assert response.status_code == 200, (
        f"Esperado HTTP 200, recebido HTTP {response.status_code}. "
        f"Resposta: {response.text}"
    )

    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_tax_withdrawal_missing_target_amount(auth_headers):
    """Verifica a validação quando target_amount está ausente."""

    response = requests.post(
        SIMULATION_URL,
        json={},
        headers={
            **auth_headers,
            "Accept": "application/json",
        },
        timeout=30,
    )

    assert response.status_code == 422, (
        f"Esperado HTTP 422, recebido HTTP {response.status_code}. "
        f"Resposta: {response.text}"
    )

    body = response.json()

    assert "detail" in body
    assert isinstance(body["detail"], list)
