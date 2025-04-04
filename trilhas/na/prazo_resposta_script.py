import os
import pandas as pd
import json
from xlsxwriter.utility import xl_col_to_name

"""
SELECT DISTINCT ON (t.tril_cd_trilha)
    t.tril_cd_trilha,
    t.tril_nm_completo, 
    t.tril_in_prazo_resposta
FROM public.trilha t
WHERE t.tril_in_ativo = B'1'
ORDER BY t.tril_cd_trilha, t.tril_cd_id DESC;

"""
# Caminho do arquivo JSON (mesma pasta do script)
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'prazo_resposta.json')

# Lê o arquivo JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Dados obtidos a partir da consulta SQL
dados = data["SELECT DISTINCT ON (t.tril_cd_trilha)\n    t.tril_cd_trilha,\n    t.tril_nm_completo, \n    t.tril_in_prazo_resposta\nFROM public.trilha t\nWHERE t.tril_in_ativo = B'1'\nORDER BY t.tril_cd_trilha, t.tril_cd_id DESC"]

# Processa os dados em DataFrame e renomeia as colunas
dados_df = pd.DataFrame(dados)
dados_df.rename(columns={
    "tril_cd_trilha": "Trilha",
    "tril_nm_completo": "Nome Trilha",
    "tril_in_prazo_resposta": "Prazo de resposta"
}, inplace=True)

# Cria agrupamento para a aba "Relatório" e calcula a média dos prazos
relatorio_df = dados_df.groupby("Prazo de resposta").size().reset_index(name='Contador')
media_prazos = dados_df["Prazo de resposta"].mean()

# Cria o arquivo Excel
output_path = os.path.join(script_dir, 'prazo_resposta.xlsx')
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
        {'header': 'Trilha', 'format': center_format},
        {'header': 'Nome Trilha', 'format': center_format},
        {'header': 'Prazo de resposta', 'format': center_format},
    ],
    'style': 'Table Style Medium 9'
})

# Aplica formatação centralizada em todas as colunas da aba "Dados"
worksheet.set_column(0, max_col - 1, None, center_format)

# Cria a aba "Relatório" e insere o agrupamento e a média
relatorio_sheet = workbook.add_worksheet('Relatório')
relatorio_sheet.write_row('A1', ['Prazo de resposta', 'Contador'], center_format)

for idx, row in relatorio_df.iterrows():
    relatorio_sheet.write(idx + 1, 0, row['Prazo de resposta'], center_format)
    relatorio_sheet.write(idx + 1, 1, row['Contador'], center_format)

# Insere a média abaixo dos dados do relatório
media_row = len(relatorio_df) + 2
relatorio_sheet.write(media_row, 0, 'Média dos prazos', center_format)
relatorio_sheet.write(media_row, 1, media_prazos, center_format)

# Salva e fecha o arquivo Excel
# Salva e fecha o arquivo Excel
writer.close()

