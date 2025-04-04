import json
import os
import re
import unicodedata

def sanitize_modalidade(modalidade):
    # Remove acentos da string
    modalidade_sem_acento = ''.join(
        c for c in unicodedata.normalize('NFKD', modalidade)
        if not unicodedata.combining(c)
    )
    # Remove hífens
    modalidade_sem_hifen = modalidade_sem_acento.replace('-', '')
    # Substitui caracteres não alfanuméricos (exceto underscore) por underscore
    modalidade_alnum = re.sub(r'[^A-Za-z0-9_]', '_', modalidade_sem_hifen)
    # Remove underscores duplicados e eventuais extremidades indesejadas
    modalidade_limpa = re.sub(r'_+', '_', modalidade_alnum).strip('_')
    return modalidade_limpa

def processar_json_por_modalidade(arquivo_json):
    # Lê o arquivo JSON mantendo sua estrutura original
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Extrai o ano do nome do arquivo base, ex: "Ano2025_consolidado_00394502000144.json"
    basename = os.path.basename(arquivo_json)
    match = re.search(r'^Ano(\d+)_consolidado_00394502000144\.json$', basename)
    if match:
        ano = match.group(1)
    else:
        print("Nome do arquivo não corresponde à estrutura esperada.")
        return

    # Obtém os valores únicos de "modalidadeNome"
    modalidades = {item.get("modalidadeNome") for item in dados if "modalidadeNome" in item}

    # Cria a pasta de saída f'{ano}/json' se não existir
    pasta_saida = os.path.join(ano, "json")
    os.makedirs(pasta_saida, exist_ok=True)
    
    for modalidade in modalidades:
        # Filtra os registros da modalidade atual
        registros_filtrados = [item for item in dados if item.get("modalidadeNome") == modalidade]
        # Sanitiza o nome da modalidade
        modalidade_segura = sanitize_modalidade(modalidade)
        # Mantém a estrutura do nome do arquivo de saída
        nome_saida = f"{modalidade_segura}_{ano}.json"
        caminho_saida = os.path.join(pasta_saida, nome_saida)
        
        # Salva o subconjunto de registros no novo arquivo JSON
        with open(caminho_saida, 'w', encoding='utf-8') as f_out:
            json.dump(registros_filtrados, f_out, ensure_ascii=False, indent=2)
        
        print(f"Arquivo salvo: {caminho_saida} com {len(registros_filtrados)} registro(s).")

if __name__ == '__main__':
    arquivo_json = "Ano2024_consolidado_00394502000144.json"
    if os.path.exists(arquivo_json):
        processar_json_por_modalidade(arquivo_json)
    else:
        print(f"Arquivo '{arquivo_json}' não encontrado.")
