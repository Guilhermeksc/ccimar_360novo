from utils.xlsx_utils import select_xlsx_multiple_sheets
from PyQt6.QtWidgets import *
import pandas as pd
import logging

def create_criterio4_patrimonio(title_text, database_manager):
    """Creates a UI component for importing XLSX data and saving it to the database."""

    # Content frame
    content_frame = QFrame()
    content_frame.setStyleSheet("""
        QFrame { 
            padding: 10px;
            background-color: #44475A; 
            border-radius: 8px;
        }
    """)

    layout = QVBoxLayout(content_frame)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # Title
    title = QLabel(title_text)
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF")
    layout.addWidget(title)

    # File path input
    file_path_input = QLineEdit()
    file_path_input.setPlaceholderText("Nenhum arquivo selecionado")
    file_path_input.setReadOnly(True)
    layout.addWidget(file_path_input)

    # Import Button
    import_button = QPushButton("Importar Tabela XLSX")
    import_button.setStyleSheet("background-color: #50fa7b; color: black; font-weight: bold; padding: 8px;")

    # Save Button
    save_button = QPushButton("Salvar no Banco de Dados")
    save_button.setStyleSheet("background-color: #8be9fd; color: black; font-weight: bold; padding: 8px;")

    # Label for status update
    values_label = QLabel("")
    values_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
    layout.addWidget(values_label)
    
    def handle_file_selection():
        """Handles file selection and loads both 'BENS MOVEIS' and 'BENS IMOVEIS' sheets."""
        sheet_names = ["BENS MOVEIS", "BENS IMOVEIS"]
        file_path, df_data = select_xlsx_multiple_sheets(sheet_names)  # Load both sheets at once

        if not file_path or df_data is None:
            values_label.setText("Erro ao carregar arquivo XLSX.")
            return

        file_path_input.setText(file_path)  # Show the file path in UI

        # Store the DataFrames for later processing
        create_criterio4_patrimonio.df_data = df_data
        values_label.setText("Arquivo carregado com sucesso.")
    
    def insert_data_to_database():
        """Handles inserting the loaded data into the database."""
        if not hasattr(create_criterio4_patrimonio, 'df_data'):
            values_label.setText("Nenhum dado carregado.")
            return

        for sheet_name, df in create_criterio4_patrimonio.df_data.items():
            if df.empty:
                continue

            for _, row in df.iterrows():
                try:
                    cod_siafi = int(float(row["COD SIAFI"]))
                except (ValueError, KeyError):
                    continue
                
                total_geral_bens_moveis = _parse_float(row.get("TOTAL GERAL")) if sheet_name == "BENS MOVEIS" else None
                importacoes_bens_moveis = _parse_float(row.get("IMPORTACOES EM ANDAMENTO - BENS MOVEIS")) if sheet_name == "BENS MOVEIS" else None
                total_geral_bens_imoveis = _parse_float(row.get("TOTAL GERAL")) if sheet_name == "BENS IMOVEIS" else None
                importacoes_bens_imoveis = _parse_float(row.get("= OBRAS EM ANDAMENTO")) if sheet_name == "BENS IMOVEIS" else None
                bens_classificar = _parse_float(row.get("= BENS IMOVEIS A CLASSIFICAR/ A REGISTRAR")) if sheet_name == "BENS IMOVEIS" else None
                
                # 🔍 Buscar todas as colunas corretamente, incluindo id_patrimonio
                query = "SELECT id_patrimonio, cod_siafi, total_geral_bens_moveis, importacoes_em_andamento_bens_moveis, total_geral_bens_imoveis, importacoes_em_andamento_bens_imoveis, bens_imoveis_a_classificar FROM criterio_patrimonio WHERE cod_siafi = ?"
                existing_record = database_manager.database_manager.execute_query(query, (cod_siafi,))

                if existing_record:
                    old_record = existing_record[0]  # Pegando o primeiro registro encontrado

                    id_patrimonio = old_record[0]  # ✅ Pegando o ID correto para evitar sobrescrita
                    print(f"🔍 ID Patrimônio Existente: {id_patrimonio} para COD SIAFI {cod_siafi}")

                    # Preservar valores antigos se os novos forem None
                    total_geral_bens_moveis = total_geral_bens_moveis if total_geral_bens_moveis is not None else old_record[2]
                    importacoes_bens_moveis = importacoes_bens_moveis if importacoes_bens_moveis is not None else old_record[3]
                    total_geral_bens_imoveis = total_geral_bens_imoveis if total_geral_bens_imoveis is not None else old_record[4]
                    importacoes_bens_imoveis = importacoes_bens_imoveis if importacoes_bens_imoveis is not None else old_record[5]
                    bens_classificar = bens_classificar if bens_classificar is not None else old_record[6]

                    update_query = """
                    UPDATE criterio_patrimonio 
                    SET total_geral_bens_moveis = ?, importacoes_em_andamento_bens_moveis = ?, 
                        total_geral_bens_imoveis = ?, importacoes_em_andamento_bens_imoveis = ?, bens_imoveis_a_classificar = ?
                    WHERE id_patrimonio = ?
                    """
                    success = database_manager.database_manager.execute_update(update_query, (
                        total_geral_bens_moveis, importacoes_bens_moveis, 
                        total_geral_bens_imoveis, importacoes_bens_imoveis, bens_classificar, id_patrimonio
                    ))
                else:
                    insert_query = """
                    INSERT INTO criterio_patrimonio (cod_siafi, total_geral_bens_moveis, importacoes_em_andamento_bens_moveis, 
                                                    total_geral_bens_imoveis, importacoes_em_andamento_bens_imoveis, bens_imoveis_a_classificar) 
                    VALUES (?, ?, ?, ?, ?, ?)"""
                    success = database_manager.database_manager.execute_update(insert_query, (
                        cod_siafi, total_geral_bens_moveis, importacoes_bens_moveis, 
                        total_geral_bens_imoveis, importacoes_bens_imoveis, bens_classificar
                    ))

                if success:
                    print(f"✅ Data successfully inserted/updated for COD SIAFI {cod_siafi}.")
                else:
                    logging.error(f"❌ Error inserting/updating data for COD SIAFI {cod_siafi}.")

        values_label.setText("Dados salvos com sucesso.")





    def _parse_float(value):
        """Converts values to float, handling NaN and empty values."""
        try:
            return float(str(value).replace(",", "")) if pd.notna(value) and str(value).strip() else None
        except ValueError:
            return None
    
    import_button.clicked.connect(handle_file_selection)
    save_button.clicked.connect(insert_data_to_database)

    layout.addWidget(import_button)
    layout.addWidget(save_button)
    layout.addWidget(values_label)

    return content_frame
