import pandas as pd

def insert_patrimonio(database_manager, df_data):
    """Inserts patrimony data from a merged DataFrame into the database."""
    
    if df_data is None or df_data.empty:
        print("Error: No valid DataFrame provided. Skipping insertion.")
        return

    # Separate data by sheet name
    df_moveis = df_data[df_data["SHEET_NAME"] == "BENS MOVEIS"].drop(columns=["SHEET_NAME"])
    df_imoveis = df_data[df_data["SHEET_NAME"] == "BENS IMOVEIS"].drop(columns=["SHEET_NAME"])

    # Merge based on COD SIAFI (outer join to keep all valid values)
    merged_df = pd.merge(df_moveis, df_imoveis, on="COD SIAFI", how="outer", suffixes=("_moveis", "_imoveis"))

    if merged_df.empty:
        print("Error: No matching COD SIAFI values found between the two sheets.")
        return

    print(f"Total matching rows for insertion: {len(merged_df)}")  # Debugging

    for _, row in merged_df.iterrows():
        cod_siafi = row["COD SIAFI"]

        if pd.isna(cod_siafi):
            print("Error: COD SIAFI is empty. Skipping insertion...")
            continue

        try:
            cod_siafi = int(float(cod_siafi))
        except ValueError:
            print(f"Error converting COD SIAFI ({cod_siafi}) to integer. Skipping...")
            continue

        # Validate existence of organization
        query = "SELECT cod_siafi FROM organizacoes_militares WHERE cod_siafi = ?"
        result = database_manager.execute_query(query, (cod_siafi,))
        if not result:
            print(f"Error: Organization not found for SIAFI code {cod_siafi}. Skipping insertion...")
            continue

        # Prepare Insert Query
        insert_query = """
        INSERT INTO criterio_patrimonio (
            cod_siafi,
            total_geral_bens_moveis,
            importacoes_em_andamento_bens_moveis,
            total_geral_bens_imoveis,
            importacoes_em_andamento_bens_imoveis,
            bens_imoveis_a_classificar
        ) VALUES (?, ?, ?, ?, ?, ?)
        """

        valores = [
            cod_siafi,
            _parse_float(row.get("TOTAL GERAL_moveis", 0)),  # From BENS MOVEIS
            _parse_float(row.get("IMPORTACOES EM ANDAMENTO - BENS MOVEIS_moveis", 0)),
            _parse_float(row.get("TOTAL GERAL_imoveis", 0)),  # From BENS IMOVEIS
            _parse_float(row.get("= OBRAS EM ANDAMENTO_imoveis", 0)),
            _parse_float(row.get("= BENS IMOVEIS A CLASSIFICAR/ A REGISTRAR_imoveis", 0)),
        ]

        success = database_manager.execute_update(insert_query, tuple(valores))
        if success:
            print(f"✅ criterio_patrimonio - Execution record successfully inserted for {cod_siafi}.")
        else:
            print(f"❌ Error inserting patrimony data for OM {cod_siafi}.")




def _parse_float(value):
    """Converts values to float, handling NaN and empty values."""
    try:
        return float(value) if pd.notna(value) else None
    except ValueError:
        return None
