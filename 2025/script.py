import pandas as pd
import os

def processar_json_para_excel(arquivo_json):
    # Carrega os dados do arquivo JSON
    dados = pd.read_json(arquivo_json)
    
    # Normaliza o campo aninhado "amparoLegal"
    df = pd.json_normalize(dados.to_dict(orient='records'))
    
    # Mapeia as colunas conforme a distribuição solicitada
    colunas_mapeadas = {
        'codigoUnidade': 'UASG',
        'nomeUnidade': 'Nome',
        'modalidadeNome': 'Modalidade',
        'dataPublicacaoPncp': 'Data Publicação',
        'srp': 'SRP',
        'numeroCompra': 'Nº',
        'anoCompra': 'Ano',
        'numeroControlePNCP': 'ID PNCP',
        'valorTotalEstimado': 'Valor Estimado',
        'valorTotalHomologado': 'valorTotalHomologado',
        'objetoCompra': 'Objeto',
        'amparoLegal.nome': 'Dispositivo Legal',
        'amparoLegal.descricao': 'Descrição Dispositivo Legal',
        'existeResultado': 'Homologado'
    }
    
    # Seleciona e renomeia as colunas conforme o mapeamento
    df_final = df[list(colunas_mapeadas.keys())].rename(columns=colunas_mapeadas)
    
    # Define o nome do arquivo Excel de saída
    nome_arquivo_excel = "consolidado.xlsx"
    
    # Cria o writer para salvar múltiplas abas
    with pd.ExcelWriter(nome_arquivo_excel) as writer:
        for modalidade in df_final['Modalidade'].unique():
            df_grupo = df_final[df_final['Modalidade'] == modalidade].copy()
            # Adiciona a coluna "Item" com numeração automática
            df_grupo.insert(0, 'Item', range(1, len(df_grupo) + 1))
            
            # Gera um nome de aba seguro
            nome_aba = modalidade.replace(" ", "_").replace("/", "_")
            df_grupo.to_excel(writer, sheet_name=nome_aba, index=False)
            print(f"Aba '{nome_aba}' criada com {len(df_grupo)} registro(s).")
    
    print(f"Arquivo '{nome_arquivo_excel}' criado com todas as abas.")

if __name__ == '__main__':
    nome_arquivo_json = "Ano2025_consolidado_00394502000144.json"
    if os.path.exists(nome_arquivo_json):
        processar_json_para_excel(nome_arquivo_json)
    else:
        print(f"Arquivo '{nome_arquivo_json}' não encontrado.")
