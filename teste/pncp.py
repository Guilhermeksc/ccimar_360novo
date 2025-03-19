import datetime
import requests
import json
from pathlib import Path

# Função para gerar os períodos de consulta
def gerar_periodos(anos=3, intervalo=360):
    """Gera períodos de consulta divididos em intervalos de no máximo 360 dias."""
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

# Função para baixar os dados da API e salvar em JSON
def baixar_dados_periodo(data_inicial, data_final, modalidade):
    base_url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": modalidade,
        "cnpj": "00394502000144",
        #"codigoUnidadeAdministrativa": "765710",
        "pagina": 1,
        "tamanhoPagina": 50
    }

    output_dir = Path(__file__).parent / "dados_contratacoes"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{modalidade}_{data_inicial}_{data_final}.json"

    all_data = []
    print(f"\n📥 Iniciando download dos dados para o período {data_inicial} ➝ {data_final} (Modalidade: {modalidade})...")

    try:
        while True:
            print(f"Baixando página {params['pagina']} para o período {data_inicial} ➝ {data_final} (Modalidade: {modalidade})...")
            response = requests.get(base_url, params=params, timeout=10)
            print(f"Status da resposta: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            if "data" in data and isinstance(data["data"], list):
                all_data.extend(data["data"])
                print(f"📊 Total de registros baixados até agora: {len(all_data)}")
            else:
                print("⚠️ Nenhum dado encontrado na resposta.")
                break

            if data.get("paginasRestantes", 0) == 0:
                break

            params["pagina"] += 1

        # Salvando os dados no arquivo JSON
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)

        print(f"✅ Dados do período {data_inicial} ➝ {data_final} (Modalidade: {modalidade}) salvos com sucesso: {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar os dados: {e}")
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar o JSON. O conteúdo recebido pode não ser um JSON válido.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

# Executar o processo para os três períodos gerados e múltiplas modalidades
if __name__ == "__main__":
    periodos = gerar_periodos(anos=3, intervalo=360)
    modalidades = [4, 6, 8, 9, 14]  # Lista de modalidades a serem consultadas

    for modalidade in modalidades:
        for data_inicial, data_final in periodos:
            baixar_dados_periodo(data_inicial, data_final, modalidade)
