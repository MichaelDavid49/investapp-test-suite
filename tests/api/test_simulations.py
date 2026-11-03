import os

import pytest
import requests


@pytest.mark.skipif(
    not os.getenv("TEST_USER") or not os.getenv("TEST_PASSWORD"),
    reason="Credenciais de teste não configuradas no ambiente.",
)
def test_simular_rendimento_mensal(base_url, auth_headers):
    """Valida a simulação de rendimento mensal da API."""

    # Arrange: prepara os dados da requisição
    payload = {
        "months": 12
    }

    # Act: envia a requisição para a API
    response = requests.post(
        f"{base_url}/api/simulate/yield-monthly",
        json=payload,
        headers=auth_headers,
        timeout=30,
    )

    # Assert: verifica o resultado
    assert response.status_code == 200, (
        f"Esperado HTTP 200, recebido {response.status_code}: "
        f"{response.text}"
    )

    resultado = response.json()

    if not isinstance(resultado, str):
        pytest.fail(
            "Formato inesperado: esperado string, "
            f"recebido {type(resultado).__name__}."
        )

    assert resultado.strip() != ""
