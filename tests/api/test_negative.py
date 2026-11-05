import os
import requests


def test_login_senha_incorreta(base_url):
    """
    CT-08-01: Validar que a API rejeita uma senha incorreta.
    HTTP esperado: 400.
    """
    usuario = os.getenv("TEST_USER")

    payload = {
        "username": usuario,
        "password": "senha_incorreta_teste_08"
    }

    response = requests.post(
        f"{base_url}/api/login",
        json=payload,
        timeout=15
    )

    print(f"\n[CT-08-01] Status obtido: {response.status_code}")
    print(f"[CT-08-01] Resposta: {response.text}")

    assert response.status_code == 400


def test_listar_investimentos_sem_token(base_url):
    """
    CT-08-02: Validar que a API bloqueia o acesso
    aos investimentos sem autenticação.
    HTTP esperado: 401.
    """

    response = requests.get(
        f"{base_url}/api/investments",
        timeout=15
    )

    print("\n[CT-08-02] Teste de acesso sem token")
    print(f"[CT-08-02] Status obtido: {response.status_code}")
    print(f"[CT-08-02] Resposta: {response.text}")

    assert response.status_code == 401


def test_criar_investimento_payload_invalido(
    base_url, auth_headers
):
    """
    CT-08-03: Validar rejeição de payload inválido.
    HTTP esperado: 422.
    """

    payload = {
        "asset_name": "CDB",
        "amount": "valor_invalido",
        "purchase_price": 1.00,
        "days_invested": 180,
        "planned_days": 720
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers,
        timeout=15
    )

    print("\n[CT-08-03] Teste de payload inválido")
    print(f"[CT-08-03] Status obtido: {response.status_code}")
    print(f"[CT-08-03] Resposta: {response.text}")

    assert response.status_code == 422


def test_criar_investimento_campo_obrigatorio_ausente(
    base_url, auth_headers
):
    """
    CT-08-04: Validar rejeição de investimento
    sem o campo obrigatório 'amount'.

    HTTP esperado: 422.
    """

    payload = {
        "asset_name": "CDB",
        "purchase_price": 1.00,
        "days_invested": 180,
        "planned_days": 720
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers,
        timeout=15
    )

    print("\n[CT-08-04] Teste de campo obrigatório ausente")
    print(f"[CT-08-04] Status obtido: {response.status_code}")
    print(f"[CT-08-04] Resposta: {response.text}")

    assert response.status_code == 422

    data = response.json()
    assert any(
        erro.get("loc") == ["body", "amount"]
        and erro.get("type") == "missing"
        for erro in data.get("detail", [])
    )


def test_listar_investimentos_token_invalido(base_url):
    """
    CT-08-05: Validar que a API rejeita
    um token JWT inválido.

    HTTP esperado: 401.
    """

    headers = {
        "Authorization": "Bearer token_invalido_teste_08"
    }

    response = requests.get(
        f"{base_url}/api/investments",
        headers=headers,
        timeout=15
    )

    print("\n[CT-08-05] Teste com token JWT inválido")
    print(f"[CT-08-05] Status obtido: {response.status_code}")
    print(f"[CT-08-05] Resposta: {response.text}")

    assert response.status_code == 401
