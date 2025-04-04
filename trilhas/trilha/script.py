import os
import pandas as pd
import json
from datetime import datetime, timedelta
from xlsxwriter.utility import xl_col_to_name

# Caminho do arquivo JSON (mesma pasta do script)
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'trilha_4_1_0.json')

# Lê o arquivo JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Dados obtidos a partir da consulta SQL
dados = data["SELECT \n    t.tril_cd_trilha,\n    nt.noau_cd_id,\n    tv.siglaom,\n    s.stat_nm_completo,\n    a.anna_nm_arquivo\nFROM public.trilha t\nINNER JOIN public.nota_auditoria nt \n    ON t.tril_cd_id = nt.tril_cd_id\nINNER JOIN public.tabela_view_om tv \n    ON tv.codom = nt.noau_cd_om \nINNER JOIN public.status s\n    ON nt.stat_cd_id = s.stat_cd_id\nINNER JOIN public.anexo_nota_auditoria a \n    ON nt.noau_cd_id = a.noau_cd_id\nWHERE t.tril_cd_trilha = '4.1.0'"]

# Processa os dados em DataFrame
dados_df = pd.DataFrame(dados)

# Renomeia as colunas para os títulos desejados
dados_df = dados_df.rename(columns={
    "tril_cd_trilha": "Trilha",
    "noau_cd_id": "NA",
    "siglaom": "OM",
    "stat_nm_completo": "Status",
    "anna_nm_arquivo": "Nome do Arquivo"
})

# Caminho para salvar o Excel
excel_path = os.path.join(script_dir, 'tabela_nome_anexo_4_1_0.xlsx')

# Cria o ExcelWriter com engine xlsxwriter
with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    dados_df.to_excel(writer, index=False, sheet_name='Trilha')
    
    workbook = writer.book
    worksheet = writer.sheets['Trilha']

    # Formato do cabeçalho (centralizado + negrito)
    header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
    
    # Aplica o formato de cabeçalho
    for col_num, value in enumerate(dados_df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # Formato de centralização
    center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
    
    # Define largura fixa para as colunas: 1 = 20, 2 = 15, 3 = 20, 4 = 50
    col_widths = {0: 10, 1: 10, 2: 20, 3:15, 4: 50}

    # Aplica o formato centralizado às células de dados
    for row_num, row_data in enumerate(dados_df.values, start=1):
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value, center_format)

    # Aplica largura fixa às colunas
    for col_num, width in col_widths.items():
        worksheet.set_column(col_num, col_num, width)

    # Define autofiltro
    worksheet.autofilter(0, 0, len(dados_df), len(dados_df.columns) - 1)
