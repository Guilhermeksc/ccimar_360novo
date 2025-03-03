from PyQt6.QtSql import QSqlQuery
import pandas as pd

def insert_organizacao_militar(database_manager, df):
    """Inserts or updates Military Organizations from a Pandas DataFrame."""
    if df.empty:
        print("Error: Empty DataFrame. No data to insert.")
        return

    required_columns = ["SIGLA SIAFI", "SIGLA_OM"]
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found in DataFrame.")
            return

    for _, row in df.iterrows():
        cod_siafi = row["SIGLA SIAFI"]
        sigla_om = str(row["SIGLA_OM"]).strip()
        nome_om = str(row["NOME_OM"]).strip()
        distrito = str(row["AREA_OM"]).strip()
        uf = str(row["UF"]).strip()

        if pd.isna(cod_siafi) or not sigla_om:
            print(f"Skipping invalid entry... ({cod_siafi}, {sigla_om})")
            continue

        try:
            cod_siafi = int(float(cod_siafi))
        except ValueError:
            print(f"Error converting SIGLA SIAFI ({cod_siafi}) to integer. Skipping...")
            continue

        query = """
        INSERT OR REPLACE INTO organizacoes_militares (cod_siafi, sigla_om, nome_om, distrito, uf)
        VALUES (?, ?, ?, ?, ?)
        """
        success = database_manager.execute_update(query, (cod_siafi, sigla_om, nome_om, distrito, uf))
        if success:
            print(f"✅ {sigla_om} ({cod_siafi}) inserted/updated successfully.")
        else:
            print(f"❌ Error inserting {sigla_om} ({cod_siafi}).")
