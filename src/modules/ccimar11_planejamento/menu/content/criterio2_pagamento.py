import pandas as pd
from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QMessageBox

def create_criterio2_pagamento(title_text, database_model):

    def select_xlsx_file():
        """Opens a file dialog to select an XLSX file and loads the data."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "Selecionar Arquivo XLSX", "", "Excel Files (*.xlsx *.xls)")

        if file_path:
            file_path_input.setText(file_path)
            try:
                # Lê a aba 'PAGAMENTO' da planilha
                df = pd.read_excel(file_path, sheet_name="PAGAMENTO")

                if df.empty:
                    QMessageBox.warning(None, "Erro", "A aba 'PAGAMENTO' está vazia ou não existe.")
                    return

                # Atualiza a referência global do DataFrame
                select_xlsx_file.df = df
                QMessageBox.information(None, "Arquivo carregado", "Planilha carregada com sucesso! Insira o índice desejado.")

            except Exception as e:
                QMessageBox.critical(None, "Erro ao abrir o arquivo", f"Erro: {str(e)}")

    def print_selected_index():
        """Prints the row corresponding to the user's selected index."""
        try:
            if not hasattr(select_xlsx_file, 'df'):
                QMessageBox.warning(None, "Erro", "Nenhum arquivo carregado. Selecione um arquivo primeiro.")
                return

            df = select_xlsx_file.df
            index_value = index_input.text().strip()

            if not index_value.isdigit():
                QMessageBox.warning(None, "Erro", "Por favor, insira um número inteiro válido como índice.")
                return

            index_value = int(index_value)

            if index_value not in df.index:
                QMessageBox.warning(None, "Erro", f"O índice {index_value} não existe na planilha.")
                return

            # Obtém a linha do índice real
            row = df.loc[index_value]

            # Exibe a linha no terminal
            print("\n📌 Linha do índice", index_value, "da aba 'PAGAMENTO':")
            print(row.to_string())

            values_label.setText(f"Linha {index_value} impressa no terminal.")

        except Exception as e:
            QMessageBox.critical(None, "Erro ao processar índice", f"Erro: {str(e)}")

    def save_to_database():
        """Saves the loaded data into the database."""
        try:
            if not hasattr(select_xlsx_file, 'df'):
                QMessageBox.warning(None, "Erro", "Nenhum arquivo carregado. Selecione um arquivo primeiro.")
                return

            df = select_xlsx_file.df

            # 🚀 Chama a função diretamente na instância correta
            database_model.insert_pagamento(df)

            QMessageBox.information(None, "Sucesso", "Os dados foram salvos no banco de dados com sucesso!")

        except Exception as e:
            QMessageBox.critical(None, "Erro ao salvar no banco de dados", f"Erro: {str(e)}")


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
    import_button.clicked.connect(select_xlsx_file)
    layout.addWidget(import_button)

    # Input for selecting index
    index_input = QLineEdit()
    index_input.setPlaceholderText("Digite o índice desejado")
    layout.addWidget(index_input)

    # Print Button
    print_button = QPushButton("Imprimir Linha no Terminal")
    print_button.setStyleSheet("background-color: #ffb86c; color: black; font-weight: bold; padding: 8px;")
    print_button.clicked.connect(print_selected_index)
    layout.addWidget(print_button)

    # Save Button
    save_button = QPushButton("Salvar no Banco de Dados")
    save_button.setStyleSheet("background-color: #8be9fd; color: black; font-weight: bold; padding: 8px;")
    save_button.clicked.connect(save_to_database)
    layout.addWidget(save_button)

    # Label for status update
    values_label = QLabel("")
    values_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
    layout.addWidget(values_label)

    return content_frame
