import requests
import json
import os

# Configuração da API
BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
CNPJ = "00394502000144"
CODIGO_MODALIDADE = 8
CODIGO_UNIDADE = 765710
TAMANHO_PAGINA = 50

# Diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "contratacoes_pncp.json")

# Cabeçalhos para simular um navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://pncp.gov.br/"
}

def consultar_api(data_inicial, data_final):
    """Consulta a API do PNCP e retorna a resposta JSON."""
    url = (
        f"{BASE_URL}?dataInicial={data_inicial}"
        f"&dataFinal={data_final}"
        f"&codigoModalidadeContratacao={CODIGO_MODALIDADE}"
        f"&cnpj={CNPJ}"
        f"&codigoUnidadeAdministrativa={CODIGO_UNIDADE}"
        f"&pagina=1"
        f"&tamanhoPagina={TAMANHO_PAGINA}"
    )

    print(f"🔍 Consultando API: {url}")

    try:
        response = requests.get(url, headers=HEADERS)

        print(f"📡 Status da resposta: {response.status_code}")

        if response.status_code == 200:
            response_json = response.json()
            num_resultados = len(response_json.get("content", []))
            print(f"📊 Registros encontrados: {num_resultados}\n")
            return response_json
        else:
            print(f"❌ Erro na requisição: {response.text}\n")
            return None
    except requests.RequestException as e:
        print(f"⚠️ Erro ao conectar com a API: {e}\n")
        return None

# Teste de uma única requisição
dados_teste = consultar_api("20240321", "20250319")

# Salvando os dados na pasta do script
if dados_teste and dados_teste.get("content"):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dados_teste, f, ensure_ascii=False, indent=4)
    print(f"📁 Dados salvos em '{OUTPUT_FILE}'.\n")
else:
    print("⚠️ Nenhum dado encontrado ou erro na API.\n")
