from PyQt6.QtSql import QSqlQuery
import pandas as pd

def insert_munic(database_manager, df):
    """Inserts municipal data from a DataFrame into the database."""
    
    if df.empty:
        print("Error: Empty DataFrame. No data to insert.")
        return

    for _, row in df.iterrows():
        cod_siafi = row["SIGLA SIAFI"]

        # Validate and convert COD SIAFI
        if pd.isna(cod_siafi):
            print("Error: COD SIAFI is empty. Skipping insertion...")
            continue

        try:
            cod_siafi = int(float(cod_siafi))  # Ensure it's an integer without .0
        except ValueError:
            print(f"Error converting COD SIAFI ({cod_siafi}) to integer. Skipping...")
            continue

        # Check if the military organization exists
        query = "SELECT cod_siafi FROM organizacoes_militares WHERE cod_siafi = ?"
        result = database_manager.execute_query(query, (cod_siafi,))
        
        if not result:
            print(f"Error: COD_SIAFI not found for code {cod_siafi}. Skipping insertion...")
            continue

        # Parse individual financial values
        despesa_autorizada = _parse_float(row["DESPESA AUTORIZADA"])
        quantidade_de_notas = _parse_int(row["QUANTIDADE_DE_NOTAS"])
        ultima_auditoria = row["ULTIMA_AUDITORIA"] if pd.notna(row["ULTIMA_AUDITORIA"]) else None

        # Ensure CODIGO_OM is inserted as an integer without .0
        codigo_om = int(float(row["CODIGO_OM"])) if pd.notna(row["CODIGO_OM"]) else None

        # Prepare the insert statement
        insert_query = """
        INSERT INTO criterio_munic (
            cod_siafi, codigo_om,
            despesa_autorizada, quantidade_de_notas, 
            ultima_auditoria
        ) VALUES (?, ?, ?, ?, ?)
        """

        valores = (
            cod_siafi,
            codigo_om,
            despesa_autorizada,
            quantidade_de_notas,
            ultima_auditoria
        )

        success = database_manager.execute_update(insert_query, valores)
        if success:
            print(f"✅ criterio_munic - Execution record successfully inserted for OM {cod_siafi}.")
        else:
            print(f"❌ Error inserting data for OM {cod_siafi}.")

def _parse_float(value):
    """Converts values to float, handling NaN and empty values."""
    try:
        return float(value) if pd.notna(value) else None
    except ValueError:
        return None

def _parse_int(value):
    """Converts values to int, handling NaN and empty values."""
    try:
        return int(float(value)) if pd.notna(value) else None
    except ValueError:
        return None
