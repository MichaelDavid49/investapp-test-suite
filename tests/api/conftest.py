import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "https://5bm1nctd1f.execute-api.us-east-1.amazonaws.com")
TEST_USER = os.getenv("TEST_USER")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


def pytest_configure(config):
    """Exibe no console os valores das variáveis de ambiente lidas na inicialização do Pytest."""
    print("\n" + "=" * 60)
    print(" [ENV CHECK] VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print(f" -> API_BASE_URL : {BASE_URL}")
    print(f" -> TEST_USER    : {TEST_USER if TEST_USER else 'NÃO DEFINIDA (None)'}")
    print(f" -> TEST_PASSWORD: {'*****' if TEST_PASSWORD else 'NÃO DEFINIDA (None)'}")

    if not TEST_USER or not TEST_PASSWORD:
        print(" [AVISO] Algumas variáveis de ambiente não foram configuradas.")
        print("          Os testes continuarão, mas chamadas autenticadas podem falhar.")
    print("=" * 60 + "\n")


@pytest.fixture(scope="session")
def base_url():
    """Retorna a URL base da API."""
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token(base_url):
    """Obtém o token Bearer JWT utilizando o usuário configurado no ambiente."""
    print(f"\n[AUTH] Autenticando com o usuário do ambiente: '{TEST_USER}'...")

    payload = {"username": TEST_USER, "password": TEST_PASSWORD}
    response = requests.post(f"{base_url}/api/login", json=payload)

    assert response.status_code == 200, (
        f"Falha na autenticação inicial com o usuário '{TEST_USER}'. "
        f"Resposta da API: {response.text}"
    )

    token = response.json().get("access_token")
    print(f"[AUTH] Sucesso! Token JWT obtido para '{TEST_USER}'.")
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Retorna o cabeçalho HTTP de autorização pré-formatado."""
    return {"Authorization": f"Bearer {auth_token}"}
