import requests

def test_listar_ativos(base_url):
    """Valida a consulta à tabela de ativos (GET /api/assets)."""
    print(f"\n[TEST_ASSETS] Consultando a lista de ativos em: {base_url}/api/assets")
    response = requests.get(f"{base_url}/api/assets")
    assert response.status_code == 200, f"Erro ao listar ativos. Resposta: {response.text}"
    data = response.json()
    assert isinstance(data, list), "O retorno da API não é uma lista."
    assert len(data) > 0, "A lista de ativos retornou vazia."
    print(f"[TEST_ASSETS] Sucesso! {len(data)} ativos encontrados.")


def test_atualizar_taxa_ativo(base_url, auth_headers):
    """Valida a atualização da taxa de um ativo específico (PUT /api/assets/{asset_id}/rate)."""
    print("\n[TEST_ASSETS] Iniciando teste de atualização de taxa de ativo...")
    response_get = requests.get(f"{base_url}/api/assets")
    assert response_get.status_code == 200, "Não foi possível listar os ativos para pegar um ID."
    ativos = response_get.json()
    assert len(ativos) > 0, "Nenhum ativo disponível para teste de atualização."
    primeiro_ativo = ativos[0]
    asset_id = primeiro_ativo.get("id") or primeiro_ativo.get("asset_id") or primeiro_ativo.get("codigo")
    print(f"[TEST_ASSETS] Ativo selecionado para teste - ID: {asset_id}")
    payload = {"rate": 0.05}
    response_put = requests.put(
        f"{base_url}/api/assets/{asset_id}/rate",
        json=payload,
        headers=auth_headers
    )
    assert response_put.status_code in [200, 204], (
        f"Falha ao atualizar a taxa do ativo {asset_id}. "
        f"Código HTTP recebido: {response_put.status_code}. Resposta: {response_put.text}"
    )
    print(f"[TEST_ASSETS] Sucesso! Taxa do ativo {asset_id} atualizada com sucesso.")
