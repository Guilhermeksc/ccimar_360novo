import requests
import datetime
import json
import os

# Configuração da API
BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
CNPJ = "00394502000144"
CODIGO_MODALIDADE = 9
CODIGO_UNIDADE = 765710
TAMANHO_PAGINA = 50

# Diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "contratacoes_pncp.json")

# Definição de cabeçalhos simulando um navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://pncp.gov.br/",
}

def consultar_api(data_inicial, data_final):
    """Consulta a API do PNCP para um intervalo de datas específico."""
    url = (
        f"{BASE_URL}?dataInicial={data_inicial}"
        f"&dataFinal={data_final}"
        f"&codigoModalidadeContratacao={CODIGO_MODALIDADE}"
        f"&cnpj={CNPJ}"
        f"&codigoUnidadeAdministrativa={CODIGO_UNIDADE}"
        f"&pagina=1"
        f"&tamanhoPagina={TAMANHO_PAGINA}"
    )

    print(f"🔍 Consultando API para o período {data_inicial} ➝ {data_final}...")
    print(f"🌐 URL utilizada: {url}")

    try:
        response = requests.get(url, headers=HEADERS)
        print(f"📡 Status da resposta: {response.status_code}")

        if response.status_code == 200:
            json_data = response.json()
            num_resultados = len(json_data.get("content", []))
            print(f"📊 Resultados encontrados: {num_resultados}\n")
            return json_data
        else:
            print(f"❌ Erro na requisição ({response.status_code}): {response.text}\n")
            return None
    except requests.RequestException as e:
        print(f"⚠️ Erro ao conectar com a API: {e}\n")
        return None

def gerar_periodos(anos=3, intervalo=360):
    """Gera períodos de consulta divididos em intervalos de no máximo 365 dias."""
    print("\n🔹 Gerando períodos de consulta...")
    hoje = datetime.date.today()
    data_final = hoje
    data_inicial = hoje - datetime.timedelta(days=anos * 360)

    periodos = []
    while data_inicial < data_final:
        prox_data_final = min(data_inicial + datetime.timedelta(days=intervalo), data_final)
        periodos.append((data_inicial.strftime("%Y%m%d"), prox_data_final.strftime("%Y%m%d")))
        print(f"📆 Período gerado: {data_inicial.strftime('%Y%m%d')} ➝ {prox_data_final.strftime('%Y%m%d')}")
        data_inicial = prox_data_final + datetime.timedelta(days=1)  # Evita sobreposição

    print(f"✅ Total de períodos gerados: {len(periodos)}\n")
    return periodos

def coletar_dados():
    """Executa as requisições para todos os períodos e consolida os resultados."""
    print("🚀 Iniciando coleta de dados...\n")
    periodos = gerar_periodos()
    resultados = []

    for data_inicial, data_final in periodos:
        dados = consultar_api(data_inicial, data_final)
        if dados and "content" in dados and len(dados["content"]) > 0:
            resultados.extend(dados["content"])  # Adiciona os resultados à lista

    print(f"✅ Coleta finalizada. Total de registros coletados: {len(resultados)}\n")
    return resultados

# Executando a coleta de dados
dados_contratacoes = coletar_dados()

# Salvando os dados na pasta do script
if dados_contratacoes:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dados_contratacoes, f, ensure_ascii=False, indent=4)
    print(f"📁 Dados salvos em '{OUTPUT_FILE}'.\n")
else:
    print("⚠️ Nenhum dado encontrado.\n")
