import os
import pandas as pd
import json
from xlsxwriter.utility import xl_col_to_name

"""
SELECT 
	na.noau_tx_numero_na,
	b."SIGLAOM",
	na.noau_ds_assunto,
	na.tril_cd_id,	
	na.noau_dt_envio,
	ua.usua_nm_completo,	
	na.noau_vl_valor,
	na.noau_vl_indicio,	
	s.stat_nm_completo,
	sr.sire_nm_completo,
	ne.niex_nm_completo,
	uc.usua_nm_completo	
FROM public.nota_auditoria na
JOIN public.status s ON na.stat_cd_id = s.stat_cd_id
JOIN public.trilha t ON na.tril_cd_id = t.tril_cd_id
JOIN public.nivel_exposicao ne ON t.niex_cd_id = ne.niex_cd_id
JOIN public.situacao_recomendacao sr on sr.sire_cd_id = na.sire_cd_id 
JOIN public.bdpes_om_temp b ON na.noau_cd_om = b."CODOM"
JOIN public.qtde_prorrogacoes qp ON na.noau_cd_id = qp.noau_cd_id
join public.usuario uc on na.usua_cd_id_cadastrador = uc.usua_cd_id
join public.usuario ua on na.usua_cd_id_avaliador = ua.usua_cd_id
where na.noau_ds_assunto like 'NOTA DE AUDITORIA - RECURSOS HUMANOS'
and na.noau_dt_envio >= '2025-01-01'
"""

# Caminho do arquivo JSON (mesma pasta do script)
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'NA_ccimar14.json')

# Lê o arquivo JSON
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Dados obtidos a partir da consulta SQL
dados = data["SELECT \n\tna.noau_tx_numero_na,\n\tb.\"SIGLAOM\",\n\tna.noau_ds_assunto,\n\tna.tril_cd_id,\t\n\tna.noau_dt_envio,\n\tna.noau_vl_valor,\n\tna.noau_vl_indicio,\t\n\ts.stat_nm_completo,\n\tsr.sire_nm_completo,\n\tne.niex_nm_completo,\n\tu.usua_nm_completo\t\nFROM public.nota_auditoria na\nJOIN public.status s ON na.stat_cd_id = s.stat_cd_id\nJOIN public.trilha t ON na.tril_cd_id = t.tril_cd_id\nJOIN public.nivel_exposicao ne ON t.niex_cd_id = ne.niex_cd_id\nJOIN public.situacao_recomendacao sr on sr.sire_cd_id = na.sire_cd_id \nJOIN public.bdpes_om_temp b ON na.noau_cd_om = b.\"CODOM\"\nJOIN public.qtde_prorrogacoes qp ON na.noau_cd_id = qp.noau_cd_id\njoin public.usuario u on na.usua_cd_id_cadastrador = u.usua_cd_id\nwhere na.noau_ds_assunto like 'NOTA DE AUDITORIA - RECURSOS HUMANOS'\nand na.noau_dt_envio >= '2025-01-01'"]

# Processa os dados em DataFrame e renomeia as colunas
dados_df = pd.DataFrame(dados)

# Cria o arquivo Excel
output_path = os.path.join(script_dir, 'ccimar14.xlsx')
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
workbook = writer.book

# Formatação centralizada
center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

# Escreve os dados na aba "Dados"
dados_df.to_excel(writer, sheet_name='Dados', index=False, startrow=0, startcol=0)
worksheet = writer.sheets['Dados']

# Define a faixa da tabela
max_row, max_col = dados_df.shape
worksheet.add_table(0, 0, max_row, max_col - 1, {
    'columns': [{'header': col, 'format': center_format} for col in dados_df.columns],
    'style': 'Table Style Medium 9'
})

# Aplica formatação centralizada em todas as colunas da aba "Dados"
worksheet.set_column(0, max_col - 1, None, center_format)

# Salva e fecha o arquivo Excel
writer.close()

