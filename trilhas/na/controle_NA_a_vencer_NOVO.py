import os
import pandas as pd
import json
from datetime import datetime, timedelta
from xlsxwriter.utility import xl_col_to_name
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from dateutil.relativedelta import relativedelta

"""
SELECT 
    nt.noau_tx_numero_na,  
    nt.noau_cd_om,
    nt.noau_ds_assunto,
    nt.noau_dt_envio,
    nt.noau_dt_prazo,
    SUM(COALESCE(qtde.qtde_prorrogacoes, 0)) AS qtde_prorrogacoes,
    nt.stat_cd_id,    
    nt.noau_dt_resposta,
    ne.niex_nm_completo,
    s.stat_nm_completo,
    b."SIGLAOM",
    b."AREAOM",
    ods.nome_setor
FROM public.nota_auditoria nt
LEFT JOIN public.status s ON nt.stat_cd_id = s.stat_cd_id
JOIN public.bdpes_om_temp b ON nt.noau_cd_om = b."CODOM"
LEFT JOIN public.gerenciador_email ge ON nt.noau_cd_om = ge.geem_cd_om
LEFT JOIN public.ods ods ON ge.geem_id_ods = ods.id
LEFT JOIN public.trilha t ON nt.tril_cd_id = t.tril_cd_id
LEFT JOIN public.nivel_exposicao ne ON t.niex_cd_id = ne.niex_cd_id
LEFT JOIN public.qtde_prorrogacoes qtde ON nt.noau_cd_id = qtde.noau_cd_id
WHERE nt.stat_cd_id NOT IN (2, 3, 5, 6, 9)
GROUP BY 
    nt.noau_tx_numero_na,  
    nt.noau_cd_om,
    nt.noau_ds_assunto,
    nt.noau_dt_envio,
    nt.noau_dt_prazo,
    nt.stat_cd_id,    
    nt.noau_dt_resposta,
    ne.niex_nm_completo,
    s.stat_nm_completo,
    b."SIGLAOM",
    b."AREAOM",
    ods.nome_setor;

"""

# Caminho do arquivo JSON (mesma pasta do script)
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'NA.json')

# Lê o arquivo JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Dados obtidos a partir da consulta SQL
dados = data["    \n    \n    SELECT \n    nt.noau_tx_numero_na,  \n    nt.noau_cd_om,\n    nt.noau_ds_assunto,\n    nt.noau_dt_envio,\n    nt.noau_dt_prazo,\n    SUM(COALESCE(qtde.qtde_prorrogacoes, 0)) AS qtde_prorrogacoes,\n    nt.stat_cd_id,    \n    nt.noau_dt_resposta,\n    ne.niex_nm_completo,\n    s.stat_nm_completo,\n    b.\"SIGLAOM\",\n    b.\"AREAOM\",\n    ods.nome_setor,\n    vo.nome_ods\nFROM public.nota_auditoria nt\nJOIN public.status s ON nt.stat_cd_id = s.stat_cd_id\nJOIN public.bdpes_om_temp b ON nt.noau_cd_om = b.\"CODOM\"\n--JOIN public.gerenciador_email ge ON nt.noau_cd_om = ge.geem_cd_om\njoin public.view_ods_por_om vo on   vo.geem_cd_om  = nt.noau_cd_om\nJOIN public.ods ods ON vo.geem_id_ods = ods.id \nJOIN public.trilha t ON nt.tril_cd_id = t.tril_cd_id\nJOIN public.nivel_exposicao ne ON t.niex_cd_id = ne.niex_cd_id\nJOIN public.qtde_prorrogacoes qtde ON nt.noau_cd_id = qtde.noau_cd_id\nWHERE nt.stat_cd_id NOT IN (2, 3, 5, 6, 9)\nGROUP BY \n    nt.noau_tx_numero_na,  \n    nt.noau_cd_om,\n    nt.noau_ds_assunto,\n    nt.noau_dt_envio,\n    nt.noau_dt_prazo,\n    nt.stat_cd_id,    \n    nt.noau_dt_resposta,\n    ne.niex_nm_completo,\n    s.stat_nm_completo,\n    b.\"SIGLAOM\",\n    b.\"AREAOM\",\n    ods.nome_setor,vo.nome_ods\n    \n    "]

# Processa os dados em DataFrame
dados_df = pd.DataFrame(dados)

# Mapeamento para AREAOM
mapping_ods = {
    'NONO DN': 'Com9DN',
    'OITAVO DN': 'Com8DN',
    'PRIMEIRO DN': 'Com1DN',
    'QUARTO DN': 'Com4DN',
    'QUINTO DN': 'Com5DN',
    'SEGUNDO DN': 'Com2DN',
    'SEXTO DN': 'Com6DN',
    'SÉTIMO DN': 'Com7DN',
    'TERCEIRO DN': 'Com3DN'
}
dados_df['AREAOM'] = dados_df['AREAOM'].str.strip().str.upper().map(mapping_ods).fillna(dados_df['AREAOM'])

# Seleciona as colunas necessárias
dados_df = dados_df[['noau_tx_numero_na', 'noau_ds_assunto', 'noau_dt_envio', 
                     'noau_dt_prazo', 'noau_dt_resposta', 'qtde_prorrogacoes', 'niex_nm_completo',
                     'stat_nm_completo', 'SIGLAOM', 'AREAOM', 'nome_setor', 'nome_ods']].copy()

# Ordena o DataFrame por data de envio (ordem crescente)
dados_df['noau_dt_envio'] = pd.to_datetime(dados_df['noau_dt_envio'])
dados_df.sort_values('noau_dt_envio', inplace=True)

def filtrar_meses_recentes(df, quantidade_meses):
    """
    Remove linhas do DataFrame cujo valor na coluna 'noau_dt_envio' pertence 
    aos 'quantidade_meses' meses mais recentes (incluindo o mês atual).
    Exibe os meses removidos e os registros afetados.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo a coluna 'noau_dt_envio' em datetime.
        quantidade_meses (int): Quantidade de meses recentes a desconsiderar (ex: 1 = mês atual).

    Retorno:
        pd.DataFrame: DataFrame com os meses recentes removidos.
    """
    # Obtém o primeiro dia do mês atual
    hoje = datetime.today()
    inicio_mes_atual = datetime(hoje.year, hoje.month, 1)

    # Gera uma lista de datas no formato 'YYYY-MM' a serem removidas
    meses_a_desconsiderar = [
        (inicio_mes_atual - relativedelta(months=i)).strftime('%Y-%m') for i in range(quantidade_meses)
    ]
    
    print(f"\nMeses desconsiderados: {meses_a_desconsiderar}")

    # Cria uma coluna auxiliar para identificar o ano-mês da data de envio
    df['ano_mes_envio'] = df['noau_dt_envio'].dt.strftime('%Y-%m')

    # Filtra os dados a serem removidos
    removidos_df = df[df['ano_mes_envio'].isin(meses_a_desconsiderar)].copy()
    if not removidos_df.empty:
        print("\nRegistros removidos:")
        print(removidos_df[['noau_tx_numero_na', 'noau_dt_envio']].to_string(index=False))
    else:
        print("\nNenhum registro removido.")

    # Filtra os dados mantidos
    df_filtrado = df[~df['ano_mes_envio'].isin(meses_a_desconsiderar)].copy()

    # Remove a coluna auxiliar
    df_filtrado.drop(columns=['ano_mes_envio'], inplace=True)

    return df_filtrado


dados_df = filtrar_meses_recentes(dados_df, quantidade_meses=2)

# Cria a coluna 'ordem' com numeração crescente
dados_df['ordem'] = range(1, len(dados_df) + 1)

# Cria as novas colunas
dados_df['Assunto'] = dados_df['noau_ds_assunto'].str.replace('NOTA DE AUDITORIA - ', '', regex=False)
dados_df['Data Envio'] = dados_df['noau_dt_envio'].dt.strftime('%d/%m/%Y')
dados_df['Data Prazo'] = pd.to_datetime(dados_df['noau_dt_prazo']).dt.strftime('%d/%m/%Y')
dados_df['Data Resposta'] = pd.to_datetime(dados_df['noau_dt_resposta'], errors='coerce').dt.strftime('%d/%m/%Y')

# Remove as colunas originais que já foram convertidas
dados_df.drop(columns=[
    'noau_ds_assunto', 'noau_dt_envio', 'noau_dt_prazo', 'noau_dt_resposta'
], inplace=True)

# Define a função de categorização (incluindo "A Vencer (Prorrogada)")
today = datetime.today()

def categorize_due_date(row):
    prazo = pd.to_datetime(row['Data Prazo'], format='%d/%m/%Y', errors='coerce')
    data_resposta = pd.to_datetime(row['Data Resposta'], format='%d/%m/%Y', errors='coerce') if row['Data Resposta'] else None
    if pd.isna(prazo):
        return 'Não identificada'
    
    hoje = datetime.today().date()
    prazo = prazo.date()

    if prazo < hoje:
        return 'Vencida'
    else:
        return 'À Vencer'


dados_df['Status NA'] = dados_df.apply(categorize_due_date, axis=1)

# Data atual apenas com data (sem hora)
hoje = pd.to_datetime(datetime.today().date())

# Cria a coluna "Dias p/ Vencer"
dados_df['Dias p/ Vencer'] = dados_df['Data Prazo'].apply(
    lambda x: (pd.to_datetime(x, format='%d/%m/%Y', errors='coerce') - hoje).days
)
# Reordena as colunas e renomeia os títulos no DataFrame principal
nova_ordem = [
    'ordem', 'noau_tx_numero_na', 'Assunto', 'SIGLAOM', 'AREAOM', 'nome_setor', 'nome_ods',
    'Data Envio', 'Data Prazo',  'Dias p/ Vencer', 'Data Resposta', 'qtde_prorrogacoes', 'niex_nm_completo', 'stat_nm_completo', 'Status NA',
]
dados_df = dados_df[nova_ordem]
dados_df.rename(columns={
    'noau_tx_numero_na': 'NA',
    'SIGLAOM': 'OM',
    'AREAOM': 'Distrito',
    'nome_setor': 'SETOR',
    'nome_ods': 'ODS',
    'qtde_prorrogacoes': 'Prorrogações',
    'niex_nm_completo': 'Risco',
    'stat_nm_completo': 'Status'
}, inplace=True)

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

    # Condicional: Se a planilha for "Dados", formata em vermelho as células de "Status NA" com valor "Vencida"
    if workbook is not None and "Status NA" in df.columns:
        status_na_index = df.columns.get_loc("Status NA")
        status_na_col = xl_col_to_name(status_na_index)
        worksheet.conditional_format(
            f"{status_na_col}2:{status_na_col}{n_rows+1}",
            {
                'type': 'cell',
                'criteria': '==',
                'value': '"Vencida"',
                'format': workbook.add_format({'font_color': 'red'})
            }
        )

    if add_totals:
        totals_rows = []
        # Agrupa pelas linhas que têm o mesmo valor em "Área"
        for area, group in df.groupby("Área"):
            sum_status = group.iloc[:, 2:].select_dtypes(include='number').sum()
            row_totals = {"Área": area, "Distrito/ODS": "Total"}
            for col in sum_status.index:
                row_totals[col] = sum_status[col]
            totals_rows.append(row_totals)
        df_totals = pd.DataFrame(totals_rows)
        start_row = n_rows + 2  # Linha logo após a tabela (deixa uma linha em branco)
        for i, (_, tot_row) in enumerate(df_totals.iterrows()):
            for j, col in enumerate(df.columns):
                value = tot_row.get(col, "")
                worksheet.write(start_row + i, j, value, center_format)

    # Formata "Dias p/ Vencer" em vermelho se valor for negativo
    if "Dias p/ Vencer" in df.columns:
        dias_index = df.columns.get_loc("Dias p/ Vencer")
        dias_col = xl_col_to_name(dias_index)
        worksheet.conditional_format(
            f"{dias_col}2:{dias_col}{n_rows+1}",
            {
                'type': 'cell',
                'criteria': '<',
                'value': 0,
                'format': workbook.add_format({'font_color': 'red'})
            }
        )
        
# Caminho do arquivo Excel
excel_path = os.path.join(script_dir, 'Consolidado_Dados.xlsx')

# Lista de ODS que devem ter planilhas específicas
lista_ods = [
    'CGCFN', 'COGESN', 'COM1DN', 'COM2DN', 'COM3DN', 'COM4DN', 'COM5DN', 'COM6DN',
    'COM7DN', 'COM8DN', 'COM9DN', 'COMEMCH', 'COMFFE', 'DGDNTM', 'DGMM', 'DGN', 'DGPM', 'SGM'
]

# Ordena o DataFrame de modo que “Vencida” fique no topo
status_order = {'Vencida': 2, 'À Vencer': 1, 'Não identificada': 0}
dados_df['status_order'] = dados_df['Status NA'].map(status_order)
dados_df.sort_values('status_order', ascending=False, inplace=True)
dados_df.drop(columns=['status_order'], inplace=True)


with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:

    workbook = writer.book
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    header_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })

    # Geração das planilhas por nome_ods (cada ODS terá uma aba própria)
    for ods in lista_ods:
        df_ods = dados_df[dados_df['ODS'] == ods]
        if not df_ods.empty:
            sheet_name = ods[:31]  # Limite de 31 caracteres no Excel
            df_ods.to_excel(writer, sheet_name=sheet_name, index=False)
            format_table(sheet_name, df_ods, [10, 13, 28, 15, 10, 12, 12, 12, 12, 12, 15, 15, 16, 11], workbook=workbook)


print(f'Arquivo Excel gerado com sucesso: {excel_path}')

import zipfile
import re

# Diretório onde os arquivos serão salvos
output_dir = os.path.join(script_dir, 'consulta_na')
os.makedirs(output_dir, exist_ok=True)

xlsx_files = []

# Geração dos arquivos XLSX por ODS
for ods in lista_ods:
    df_ods = dados_df[dados_df['ODS'] == ods]
    if not df_ods.empty:
        nome_arquivo = re.sub(r'[\\/*?:"<>|]', "_", ods[:50]) + ".xlsx"
        caminho_arquivo = os.path.join(output_dir, nome_arquivo)
        with pd.ExcelWriter(caminho_arquivo, engine='xlsxwriter') as writer:
            df_ods.to_excel(writer, sheet_name=ods[:31], index=False)
            workbook = writer.book
            center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
            format_table(ods[:31], df_ods, [10, 13, 28, 15, 10, 12, 12, 12, 12, 12, 15, 15, 16, 11], workbook=workbook)
        xlsx_files.append(caminho_arquivo)

# Geração dos arquivos XLSX por SETOR
setores_unicos = dados_df['SETOR'].dropna().unique()

for setor in setores_unicos:
    df_setor = dados_df[dados_df['SETOR'] == setor]
    if not df_setor.empty:
        nome_arquivo = re.sub(r'[\\/*?:"<>|]', "_", setor[:50]) + ".xlsx"
        caminho_arquivo = os.path.join(output_dir, nome_arquivo)
        with pd.ExcelWriter(caminho_arquivo, engine='xlsxwriter') as writer:
            df_setor.to_excel(writer, sheet_name='Consulta NA', index=False)
            workbook = writer.book
            center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
        
            workbook = writer.book
            center_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            header_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })

            format_table('Consulta NA', df_setor, [10, 13, 28, 15, 10, 12, 12, 12, 12, 12, 15, 15, 16, 11], workbook=workbook)

        xlsx_files.append(caminho_arquivo)

# Cria o arquivo zip com todos os arquivos XLSX gerados
zip_path = os.path.join(script_dir, 'consulta_na.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path in xlsx_files:
        arcname = os.path.basename(file_path)
        zipf.write(file_path, arcname)

print(f'\nTodos os arquivos XLSX foram salvos em: {output_dir}')
print(f'Arquivo ZIP criado com sucesso em: {zip_path}')

# Geração da tabela de contagem de NA por SETOR
# Geração da tabela de contagem de NA por SETOR, incluindo as colunas NA Vencidas e NA À vencer
contagem_por_setor = dados_df.groupby('SETOR').agg(
    Quantidade_de_NA=('NA', 'count'),
    NA_Vencidas=('Status NA', lambda x: (x == 'Vencida').sum()),
    NA_A_vencer=('Status NA', lambda x: (x == 'À Vencer').sum())
).reset_index()

contagem_por_setor.rename(columns={'NA': 'Quantidade de NA'}, inplace=True)

# Caminho para salvar a planilha de contagem
contagem_path = os.path.join(script_dir, 'consulta_na', 'Contagem_NA_por_Setor.xlsx')
with pd.ExcelWriter(contagem_path, engine='xlsxwriter') as writer:
    contagem_por_setor.to_excel(writer, sheet_name='Contagem', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Contagem']
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    worksheet.set_column('A:A', 50)
    worksheet.set_column('B:B', 20)
    for col_num, value in enumerate(contagem_por_setor.columns):
        worksheet.write(0, col_num, value, header_format)
    for row in range(1, len(contagem_por_setor) + 1):
        for col in range(2):
            worksheet.write(row, col, contagem_por_setor.iloc[row - 1, col], cell_format)

# Adiciona o novo arquivo ao ZIP
with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(contagem_path, arcname='Contagem_NA_por_Setor.xlsx')

print(f'Tabela "Contagem_NA_por_Setor.xlsx" salva em: {contagem_path}')
