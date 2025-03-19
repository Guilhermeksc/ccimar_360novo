import pandas as pd
import os

# Obtém o diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define o caminho do arquivo CSV dentro da pasta do script
file_path = os.path.join(script_dir, "trilhas.csv")

# Verifica se o arquivo existe
if not os.path.isfile(file_path):
    print(f"Erro: O arquivo 'trilhas.csv' não foi encontrado em {script_dir}. Verifique e tente novamente.")
    exit()

# Carregar o arquivo CSV garantindo a correta separação das colunas
df = pd.read_csv(file_path, delimiter="|")

# Remover a área 'ATOS DE PESSOAL'
df = df[df["area_nm_completo"] != "ATOS DE PESSOAL"]

# Remover duplicatas considerando apenas o maior 'tril_cd_id' para cada 'tril_cd_trilha'
df = df.loc[df.groupby("tril_cd_trilha")["tril_cd_id"].idxmax()]

# Mapeamento das colunas para os novos nomes e tamanhos desejados
columns_mapping = {
    "tril_cd_id": ("ID AUDCONT", 10),
    "tril_cd_trilha": ("Trilha ID", 10),
    "tril_nm_completo": ("Nome", 80),
    "tril_in_aprovado": ("Aprovado", 15),
    "niex_nm_completo": ("Nível de risco", 10)
}

# Selecionar e renomear as colunas
df_selected = df[list(columns_mapping.keys())].rename(columns={k: v[0] for k, v in columns_mapping.items()})

# Converter valores da coluna "Aprovado"
df_selected["Aprovado"] = df_selected["Aprovado"].map({1: "Aprovado", 0: "Não aprovado"}).fillna("Desconhecido")

# Contar os valores únicos da coluna "area_nm_completo"
area_counts = df["area_nm_completo"].value_counts().reset_index()
area_counts.columns = ["Area", "Quantidade"]

# Caminho do arquivo de saída dentro da mesma pasta do script
output_file = os.path.join(script_dir, "trilhas_analisadas.xlsx")

# Criar um arquivo Excel
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    workbook = writer.book  # Referência ao workbook

    # Criar a aba de contagem de áreas
    area_counts.to_excel(writer, sheet_name="Contador de Áreas", index=False, startrow=0)
    
    # Ajustar a largura das colunas na aba "Contador de Áreas"
    worksheet = writer.sheets["Contador de Áreas"]
    worksheet.set_column(0, 0, 50)  # Largura da coluna "Area"
    worksheet.set_column(1, 1, 15)  # Largura da coluna "Quantidade"

    # Criar aba para registrar os riscos
    risk_sheet_name = "Riscos"
    risk_worksheet = writer.book.add_worksheet(risk_sheet_name)
    writer.sheets[risk_sheet_name] = risk_worksheet
    
    # Adicionar linha de TOTAL no final da aba "Contador de Áreas"
    total_row = len(area_counts) + 1  # Linha onde o total será inserido
    worksheet.write(total_row, 0, "TOTAL")  # Escrever "TOTAL"
    worksheet.write_formula(total_row, 1, f"=SUM(B2:B{total_row})")  # Fórmula de soma

    # Criar uma aba para cada área encontrada
    for area in sorted(df["area_nm_completo"].dropna().unique()):  # Ordenar as áreas alfabeticamente
        sheet_name = area[:31]  # Garantir que o nome da aba não exceda 31 caracteres
        area_df = df_selected[df["area_nm_completo"] == area].sort_values(by="Nome")  # Ordenação por tril_nm_completo
        
        # Escrever a aba no Excel
        area_df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]

        # Ajustar a largura das colunas
        for col_idx, (col_name, width) in enumerate(columns_mapping.values()):
            worksheet.set_column(col_idx, col_idx, width)

    # Adicionar tabelas individuais por risco dentro da aba "Contador de Áreas"
    row_position = len(area_counts) + 4  # Posição inicial após a tabela principal
        
    risk_row = 0  # Linha inicial na aba "Riscos"
    print("Iniciando a criação das tabelas de risco...")
    
    risk_order = {"MUITO ALTO": 1, "ALTO": 2, "MÉDIO": 3, "BAIXO": 4, "MUITO BAIXO": 5}
    
    for area in sorted(df["area_nm_completo"].dropna().unique()):
        print(f"Processando área: {area}")
        risk_worksheet.merge_range(risk_row, 0, risk_row, 1, area, workbook.add_format({'bold': True, 'align': 'center', 'border': 1}))
        risk_row += 1
        
        risk_worksheet.write(risk_row, 0, "Risco", workbook.add_format({'bold': True, 'border': 1}))
        risk_worksheet.write(risk_row, 1, "Quantidade", workbook.add_format({'bold': True, 'border': 1}))
        risk_row += 1
        
        risk_counts = (
            df[df["area_nm_completo"] == area]["niex_nm_completo"]
            .value_counts()
            .reset_index()
        )
        risk_counts.columns = ["Risco", "Quantidade"]
        
        risk_counts["order"] = risk_counts["Risco"].map(risk_order)
        risk_counts = risk_counts.sort_values(by="order", ascending=True).drop(columns=["order"])
        
        print(f"Riscos encontrados para {area}: {risk_counts.shape[0]} linhas")
        
        for _, row in risk_counts.iterrows():
            print(f"Adicionando risco: {row['Risco']} - Quantidade: {row['Quantidade']}")
            risk_worksheet.write(risk_row, 0, row["Risco"], workbook.add_format({'border': 1}))
            risk_worksheet.write(risk_row, 1, row["Quantidade"], workbook.add_format({'border': 1, 'align': 'center'}))
            risk_row += 1
        
        risk_row += 1  # Adicionar espaço entre as áreas
    
    print("Finalização da criação das tabelas de risco.")

print(f"Arquivo gerado com sucesso: {output_file}")