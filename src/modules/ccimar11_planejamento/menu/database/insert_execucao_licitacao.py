from PyQt6.QtSql import QSqlQuery
import pandas as pd

def insert_execucao_licitacao(database_manager, df):
    """Inserts execution data from a DataFrame into the database, including total execution value."""
    
    if df.empty:
        print("Error: Empty DataFrame. No data to insert.")
        return

    for _, row in df.iterrows():
        cod_siafi = row["COD SIAFI"]

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
        valor_convite = _parse_float(row["VALOR CONVITE"])
        valor_tomada_preco = _parse_float(row["VALOR TP"])
        valor_concorrencia = _parse_float(row["VALOR CONC"])
        valor_dispensa = _parse_float(row["VALOR DISP LICIT"])
        valor_inexigibilidade = _parse_float(row["VALOR INEXIG"])
        valor_nao_se_aplica = _parse_float(row["VALOR NÃO SE APLICA"])
        valor_suprimento_fundos = _parse_float(row["VALOR SF"])
        valor_regime_diferenciado = _parse_float(row["VALOR REG DIF CONT PUB"])
        valor_cons = _parse_float(row["VALOR CONS"])
        valor_pregao_eletronico = _parse_float(row["VALOR PREGAO"])
        valor_credenciamento = _parse_float(row["VALOR CRED"])

        # Calculate the total execution value
        execucao_licitacao = sum(
            v for v in [
                valor_convite, valor_tomada_preco, valor_concorrencia, 
                valor_dispensa, valor_inexigibilidade, valor_nao_se_aplica, 
                valor_suprimento_fundos, valor_regime_diferenciado, valor_cons, 
                valor_pregao_eletronico, valor_credenciamento
            ] if v is not None
        )

        # Prepare the insert statement
        insert_query = """
        INSERT INTO criterio_execucao_licitacao (
            cod_siafi, valor_convite, valor_tomada_preco, valor_concorrencia, 
            valor_dispensa, valor_inexigibilidade, valor_nao_se_aplica, 
            valor_suprimento_fundos, valor_regime_diferenciado, valor_cons, 
            valor_pregao_eletronico, valor_credenciamento, valor_total_execucao_licitacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        valores = (
            cod_siafi,
            valor_convite,
            valor_tomada_preco,
            valor_concorrencia,
            valor_dispensa,
            valor_inexigibilidade,
            valor_nao_se_aplica,
            valor_suprimento_fundos,
            valor_regime_diferenciado,
            valor_cons,
            valor_pregao_eletronico,
            valor_credenciamento,
            execucao_licitacao
        )

        success = database_manager.execute_update(insert_query, valores)
        if success:
            print(f"✅ criterio_execucao_licitacao - Execution record successfully inserted for OM {cod_siafi}.")
        else:
            print(f"❌ Error inserting execution data for OM {cod_siafi}.")

def _parse_float(value):
    """Converts values to float, handling NaN and empty values."""
    try:
        return float(value) if pd.notna(value) else None
    except ValueError:
        return None
