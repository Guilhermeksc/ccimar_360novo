import os
import pandas as pd
import json
from xlsxwriter.utility import xl_col_to_name

"""
SELECT LU.IP, 
LU.NIP,
LU.POSTO_GRAD, 
LU.NOME,
COUNT(LU.NIP) AS NUM_ACESSOS,
TO_CHAR(LU.LOG_DATETIME, 'YYYY-MM') AS DATAS,
LU.OM_ID, 
OM.INDICATIVO_NAVAL,
OM.SIGLA 
FROM GESTORIA.LOG_USUARIO LU 
INNER JOIN GESTORIA.OM OM ON LU.OM_ID=OM.ID
WHERE TO_CHAR(LOG_DATETIME, 'YYYY-MM-DD') >=('2024-01%')
--OR TO_CHAR(LOG_DATETIME, 'YYYY-MM-DD') LIKE('2023-01%')
AND LU.OM_ID = 10004
GROUP BY LU.IP, LU.NIP,LU.POSTO_GRAD, 
LU.NOME, TO_CHAR(LU.LOG_DATETIME, 'YYYY-MM'),LU.OM_ID, 
OM.INDICATIVO_NAVAL,OM.SIGLA 
ORDER BY LU.IP DESC
"""

# Caminho do arquivo JSON (mesma pasta do script)
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'acesso_quaestor.json')

# Lê o arquivo JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Obtém a chave (cabeçalho) do arquivo JSON e seus dados correspondentes
chave = list(data.keys())[0]
dados = data[chave]

# Processa os dados em DataFrame
dados_df = pd.DataFrame(dados)

# Cria o arquivo Excel
output_path = os.path.join(script_dir, 'acesso_quaestor.xlsx')
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
workbook = writer.book

# Formatação centralizada
center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

# Escreve os dados na aba "Dados"
dados_df.to_excel(writer, sheet_name='Dados', index=False, startrow=0, startcol=0)
worksheet = writer.sheets['Dados']

# Define a faixa da tabela
max_row, max_col = dados_df.shape
# A tabela inclui cabeçalho na linha 0 e dados de 1 até max_row
worksheet.add_table(0, 0, max_row, max_col - 1, {
    'columns': [
        {'header': 'IP', 'format': center_format},
        {'header': 'NIP', 'format': center_format},
        {'header': 'POSTO_GRAD', 'format': center_format},
        {'header': 'NOME', 'format': center_format},
        {'header': 'NUM_ACESSOS', 'format': center_format},
        {'header': 'DATAS', 'format': center_format},
        {'header': 'OM_ID', 'format': center_format},
        {'header': 'INDICATIVO_NAVAL', 'format': center_format},
        {'header': 'SIGLA', 'format': center_format},        
    ],
    'style': 'Table Style Medium 9'
})

# Função para formatar a tabela e, se indicado, adicionar linhas de totais abaixo da tabela
def format_table(sheet_name, df, col_widths, add_totals=False, workbook=None):
    worksheet = writer.sheets[sheet_name]
    # Define a largura de cada coluna
    for idx, width in enumerate(col_widths):
        col_letter = xl_col_to_name(idx)
        worksheet.set_column(f"{col_letter}:{col_letter}", width)
    n_rows, n_cols = df.shape
    last_col = xl_col_to_name(n_cols - 1)
    table_range = f"A1:{last_col}{n_rows + 1}"
    # Define os cabeçalhos com o formato diferenciado
    columns = [{"header": col, "format": header_format} for col in df.columns]
    worksheet.add_table(table_range, {
        'style': 'Table Style Medium 9',
        'columns': columns,
        'autofilter': True
    })
    worksheet.freeze_panes(1, 0)
    # Aplica formatação centralizada às células de dados
    for row in range(1, n_rows + 1):
        for col in range(n_cols):
            value = df.iloc[row - 1, col]
            if pd.isna(value):
                value = ""
            worksheet.write(row, col, value, center_format)
            
# Aplica formatação centralizada em todas as colunas da aba "Dados"
worksheet.set_column(0, max_col - 1, None, center_format)

# Salva e fecha o arquivo Excel
writer.close()

