import json
import requests
from pathlib import Path

def baixar_contratos():
    url = "https://contratos.comprasnet.gov.br/api/contrato/unidades"
    caminho_saida = Path(__file__).parent / "contratos_ativos_uasg.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        dados = response.json()
        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print("✅ Arquivo baixado e salvo com sucesso.")
    except requests.exceptions.RequestException as e:
        print(f"💥 Erro na requisição: {e}")

if __name__ == "__main__":
    baixar_contratos()
