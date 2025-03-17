from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QComboBox, QLabel, QLineEdit
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import datetime
from utils.styles.style_add_button import add_button_func

def create_tab_2_01(icons):
    icons = icons
    
    widget = QWidget()
    main_layout = QVBoxLayout(widget)
        
    # Layout horizontal: campo de inputs à esquerda e área de visualização à direita
    h_layout = QHBoxLayout()
    
    input_widget = QWidget()
    input_widget.setFixedWidth(280)
    input_layout = QVBoxLayout(input_widget)
    
    def add_input(layout, label_text, default_value="", validator_pattern=None):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        if validator_pattern:
            regex = QRegularExpression(validator_pattern)
            validator = QRegularExpressionValidator(regex)
            input_field.setValidator(validator)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    # Adiciona os campos de input
    data_inicial_default = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y%m%d')
    data_inicial_input = add_input(input_layout, "Data Inicial * (YYYYMMDD):", data_inicial_default, "[0-9]{8}")
    data_final_default = datetime.datetime.now().strftime('%Y%m%d')
    data_final_input = add_input(input_layout, "Data Final * (YYYYMMDD):", data_final_default, "[0-9]{8}")
    cnpj_input = add_input(input_layout, "CNPJ (default: 00394502000144):", "00394502000144", "[0-9]{14}")
    codigo_unidade_input = add_input(input_layout, "Código UASG (6 digits):", "", "[0-9]{6}")
    
    # Botão para Modalidade de Contratação com QComboBox
    modalidade_label = QLabel("Modalidade de Contratação:")
    input_layout.addWidget(modalidade_label)
    modalidade_combobox = QComboBox()
    modalidades = [
        "1 - Leilão - Eletrônico",
        "2 - Diálogo Competitivo",
        "3 - Concurso",
        "4 - Concorrência - Eletrônica",
        "5 - Concorrência - Presencial",
        "6 - Pregão - Eletrônico",
        "7 - Pregão - Presencial",
        "8 - Dispensa",
        "9 - Inexigibilidade",
        "10 - Manifestação de Interesse",
        "11 - Pré-qualificação",
        "12 - Credenciamento",
        "13 - Leilão - Presencial",
        "14 - Inaplicabilidade da Licitação"
    ]
    modalidade_combobox.addItems(modalidades)
    input_layout.addWidget(modalidade_combobox)
    input_layout.addStretch()

    button_layout = QHBoxLayout()
    button_layout.addStretch()  # Espaço antes do botão
    btn_consulta_ata = add_button_func("Consultar Atas", "api", on_consultar_button_click, button_layout, icons, tooltip="Clique para consultar as atas", button_size=(200, 40))
    button_layout.addStretch()  # Espaço depois do botão

    input_layout.addLayout(button_layout)  # Adicionar botão centralizado ao input_layout
    input_layout.addStretch()  # Espaço depois do botão

    # Área de visualização de dados
    visualization_widget = QPlainTextEdit()
    visualization_widget.setReadOnly(True)
    
    h_layout.addWidget(input_widget)
    h_layout.addWidget(visualization_widget)

    main_layout.addLayout(h_layout)

    return widget

def on_consultar_button_click():
    pass