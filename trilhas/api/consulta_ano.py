import os
import json
import requests
from pathlib import Path
from time import sleep

def consultar_compras_por_lote(cnpj: str, ano: int, intervalo: int = 1000):
    base_url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{{sequencial}}"
    pasta_saida = Path.cwd() / str(ano)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    sequencial_inicial = 1
    falhas = {}

    while True:
        resultados = {}
        falhas_lote = []
        sequencial_final = sequencial_inicial + intervalo - 1

        for sequencial in range(sequencial_inicial, sequencial_final + 1):
            url = base_url.format(sequencial=sequencial)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    resultados[str(sequencial)] = response.json()
                    print(f"✅ Endpoint {sequencial} consultado com sucesso.")
                elif response.status_code == 404:
                    falhas_lote.append(sequencial)
                    print(f"⚠️ Endpoint {sequencial} retornou 404.")
                else:
                    print(f"❌ Erro inesperado em {sequencial}: {response.status_code}")
            except Exception as e:
                print(f"💥 Erro em {sequencial}: {str(e)}")
                falhas_lote.append(sequencial)

            sleep(0.05)  # evitar sobrecarregar o servidor

        if resultados:
            nome_arquivo = f"Ano{ano}Sequencial_{sequencial_inicial}_{sequencial_final}_{cnpj}.json"
            with open(pasta_saida / nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)

        if falhas_lote:
            falhas[str(sequencial_inicial)] = falhas_lote
            nome_falha = f"Ano{ano}Sequencial_{sequencial_inicial}_{sequencial_final}_{cnpj}_404.json"
            with open(pasta_saida / nome_falha, "w", encoding="utf-8") as f:
                json.dump(falhas_lote, f, ensure_ascii=False, indent=2)

        if not resultados and not falhas_lote:
            print(f"🏁 Fim da busca para {ano}")
            break

        sequencial_inicial += intervalo

# Exemplo de uso:
consultar_compras_por_lote(cnpj="00394502000144", ano=2025)
