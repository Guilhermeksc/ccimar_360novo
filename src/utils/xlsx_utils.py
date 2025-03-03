import pandas as pd
from PyQt6.QtWidgets import QFileDialog, QMessageBox

def select_xlsx_multiple_sheets(sheet_names):
    """
    Opens a file dialog to select an XLSX file and loads multiple specified sheets.

    Args:
        sheet_names (list): A list of sheet names to be loaded.

    Returns:
        tuple: (file_path, dict_of_dataframes) where dict_of_dataframes contains {sheet_name: dataframe}
    """
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Selecionar Arquivo XLSX", "", "Excel Files (*.xlsx *.xls)")

    if not file_path:
        return None, None  # No file selected

    try:
        # Load only specified sheets
        dfs = pd.read_excel(file_path, sheet_name=sheet_names)

        # Check for empty sheets
        for sheet_name in sheet_names:
            if sheet_name not in dfs or dfs[sheet_name].empty:
                QMessageBox.warning(None, "Erro", f"A aba '{sheet_name}' está vazia ou não existe.")
                return None, None

        QMessageBox.information(None, "Sucesso", "Planilhas carregadas com sucesso! Insira o índice desejado.")
        return file_path, dfs

    except Exception as e:
        QMessageBox.critical(None, "Erro ao abrir o arquivo", f"Erro: {str(e)}")
        return None, None


def select_xlsx_file(sheet_name):
    """Opens a file dialog to select an XLSX file and loads the data from the specified sheet."""
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Selecionar Arquivo XLSX", "", "Excel Files (*.xlsx *.xls)")

    if not file_path:
        return None, None  # No file selected

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        if df.empty:
            QMessageBox.warning(None, "Erro", f"A aba '{sheet_name}' está vazia ou não existe.")
            return None, None

        QMessageBox.information(None, "Arquivo carregado", "Planilha carregada com sucesso! Insira o índice desejado.")
        return file_path, df

    except Exception as e:
        QMessageBox.critical(None, "Erro ao abrir o arquivo", f"Erro: {str(e)}")
        return None, None

def print_selected_index(df, index_value, sheet_name):
    """Prints the row corresponding to the user's selected index from a specific sheet."""
    try:
        if df is None:
            QMessageBox.warning(None, "Erro", "Nenhum arquivo carregado. Selecione um arquivo primeiro.")
            return

        if not index_value.strip().isdigit():
            QMessageBox.warning(None, "Erro", "Por favor, insira um número inteiro válido como índice.")
            return

        index_value = int(index_value)

        if index_value not in df.index:
            QMessageBox.warning(None, "Erro", f"O índice {index_value} não existe na aba '{sheet_name}'.")
            return

        row = df.loc[index_value]

        print(f"\n📌 Linha do índice {index_value} da aba '{sheet_name}':")
        print(row.to_string())

        return f"Linha {index_value} impressa no terminal."

    except Exception as e:
        QMessageBox.critical(None, "Erro ao processar índice", f"Erro: {str(e)}")
        return None

def save_to_database(df, insert_function):
    """Saves the loaded data into the database using a provided insert function."""
    try:
        if df is None or df.empty:
            QMessageBox.warning(None, "Erro", "Nenhum dado válido foi carregado. Selecione um arquivo primeiro.")
            print("Error: DataFrame is None or empty.")  # Debugging
            return

        # Ensure correct data format before passing to the database function
        if isinstance(df, pd.DataFrame):
            print(f"Inserting {len(df)} rows into the database.")  # Debugging

            # ✅ Convert DataFrame to a list of dictionaries (if needed)
            data_to_insert = df.to_dict(orient="records")  # [{'COD SIAFI': 791500.0}, ...]

            # Debug: Show first few records
            print("First 5 records to insert:", data_to_insert[:5])

            # 🔥 Try inserting the cleaned data
            insert_function(data_to_insert)  # Call the provided function

            QMessageBox.information(None, "Sucesso", "Os dados foram salvos no banco de dados com sucesso!")
        else:
            QMessageBox.critical(None, "Erro ao salvar", "Formato inválido de dados. Esperado DataFrame.")
            print("Error: Data format is invalid.")  # Debugging

    except Exception as e:
        QMessageBox.critical(None, "Erro ao salvar no banco de dados", f"Erro: {str(e)}")
        print(f"Database insertion error: {str(e)}")  # Debugging
