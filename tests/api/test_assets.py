import requests


def test_listar_ativos(base_url):
    """Valida a consulta pública de taxas de ativos sem autenticação."""
    print(f"\n[TEST_ASSETS] Consultando a lista de ativos em: {base_url}/api/assets")
    response = requests.get(f"{base_url}/api/assets")

    assert response.status_code == 200, f"Erro ao listar ativos: {response.text}"
    ativos = response.json()
    assert isinstance(ativos, list), "A resposta esperada deve ser uma lista de ativos."
    assert len(ativos) > 0, "A lista de ativos retornou vazia."
    print(f"[TEST_ASSETS] Sucesso! {len(ativos)} ativos encontrados.")


def test_atualizar_taxa_ativo(base_url, auth_headers):
    """Valida a atualização da taxa de um ativo (PUT /api/assets)."""
    print("\n[TEST_ASSETS] Iniciando teste de atualização de taxa de ativo...")

    # 1. Obtém os ativos existentes
    response_get = requests.get(f"{base_url}/api/assets")
    assert response_get.status_code == 200, "Não foi possível listar os ativos."

    ativos = response_get.json()
    assert len(ativos) > 0, "Nenhum ativo disponível para atualização."

    primeiro_ativo = ativos[0]
    nome_ativo = primeiro_ativo.get("asset_name", "Poupança")
    print(f"[TEST_ASSETS] Atualizando taxa para o ativo: '{nome_ativo}'")

    # 2. Payload exatamente como exigido pela API (asset_name e annual_rate)
    payload = {
        "asset_name": nome_ativo,
        "annual_rate": 7.50
    }

    # 3. Requisição PUT para atualizar
    response_put = requests.put(
        f"{base_url}/api/assets",
        json=payload,
        headers=auth_headers
    )

    print(f"[TEST_ASSETS] Status da resposta: {response_put.status_code}")
    print(f"[TEST_ASSETS] Corpo da resposta: {response_put.text}")

    assert response_put.status_code in [200, 204], (
        f"Falha ao atualizar a taxa do ativo '{nome_ativo}'. "
        f"Código HTTP: {response_put.status_code}. Resposta: {response_put.text}"
    )
    print(f"[TEST_ASSETS] Taxa de '{nome_ativo}' atualizada com sucesso!")
