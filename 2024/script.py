import pandas as pd
import os

def xl_col_to_name(n):
    """Converte índice de coluna (0-index) para nome de coluna Excel (A, B, ..., Z, AA, AB, ...)"""
    result = ""
    while n >= 0:
        result = chr(n % 26 + ord('A')) + result
        n = n // 26 - 1
    return result

def format_table(writer, sheet_name, df, col_widths, add_totals=False):
    workbook = writer.book
    header_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    worksheet = writer.sheets[sheet_name]
    
    # Define a largura de cada coluna
    for idx, width in enumerate(col_widths):
        col_letter = xl_col_to_name(idx)
        worksheet.set_column(f"{col_letter}:{col_letter}", width)
    
    n_rows, n_cols = df.shape
    last_col = xl_col_to_name(n_cols - 1)
    table_range = f"A1:{last_col}{n_rows + 1}"
    
    # Cria a lista de cabeçalhos formatados
    columns = [{"header": col, "format": header_format} for col in df.columns]
    worksheet.add_table(table_range, {
        'style': 'Table Style Medium 9',
        'columns': columns,
        'autofilter': True
    })
    worksheet.freeze_panes(1, 0)

def processar_json_para_excel(arquivo_json):
    # Carrega e normaliza os dados
    dados = pd.read_json(arquivo_json)
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
    df_final = df[list(colunas_mapeadas.keys())].rename(columns=colunas_mapeadas)
    
    nome_arquivo_excel = "consolidado.xlsx"
    with pd.ExcelWriter(nome_arquivo_excel, engine='xlsxwriter') as writer:
        for modalidade in df_final['Modalidade'].unique():
            df_grupo = df_final[df_final['Modalidade'] == modalidade].copy()
            df_grupo.insert(0, 'Item', range(1, len(df_grupo) + 1))
            nome_aba = modalidade.replace(" ", "_").replace("/", "_")
            df_grupo.to_excel(writer, sheet_name=nome_aba, index=False)
            
            # Definindo larguras de coluna (ajuste conforme necessário)
            col_widths = [10] * len(df_grupo.columns)
            format_table(writer, nome_aba, df_grupo, col_widths)
            print(f"Aba '{nome_aba}' criada com {len(df_grupo)} registro(s).")
    print(f"Arquivo '{nome_arquivo_excel}' criado com todas as abas.")

if __name__ == '__main__':
    nome_arquivo_json = "Ano2024_consolidado_00394502000144.json"
    if os.path.exists(nome_arquivo_json):
        processar_json_para_excel(nome_arquivo_json)
    else:
        print(f"Arquivo '{nome_arquivo_json}' não encontrado.")
