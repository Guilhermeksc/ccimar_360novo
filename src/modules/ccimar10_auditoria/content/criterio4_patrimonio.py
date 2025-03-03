from utils.xlsx_utils import select_xlsx_multiple_sheets, save_to_database
from PyQt6.QtWidgets import *

def create_criterio4_patrimonio(title_text, database_model):
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

    # Input for selecting index
    index_input = QLineEdit()
    index_input.setPlaceholderText("Digite o índice desejado")
    layout.addWidget(index_input)

    # Print Button
    print_button = QPushButton("Imprimir Linha no Terminal")
    print_button.setStyleSheet("background-color: #ffb86c; color: black; font-weight: bold; padding: 8px;")

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
            return

        file_path_input.setText(file_path)  # Show the file path in UI

        # Store the DataFrames for later processing
        create_criterio4_patrimonio.df_data = df_data

    def handle_save_to_database():
        if hasattr(create_criterio4_patrimonio, 'df_data'):
            save_to_database(create_criterio4_patrimonio.df_data, database_model.insert_patrimonio)



    import_button.clicked.connect(handle_file_selection)
    save_button.clicked.connect(handle_save_to_database)

    layout.addWidget(import_button)
    layout.addWidget(save_button)
    layout.addWidget(values_label)

    return content_frame
