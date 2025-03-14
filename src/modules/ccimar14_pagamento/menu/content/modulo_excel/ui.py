import os
import random
import re
import glob
import pandas as pd
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QWidget
)

def generate_random_os():
    numero = random.randint(1, 9999)
    numero_str = f"{numero:03d}" if random.choice([True, False]) else str(numero)
    ano = random.choice([2024, 24, 2025, 25])
    ano_str = str(ano)
    sep = random.choice(["/", "-", "_", "\\"])
    if random.choice([True, False]):
        sep = f" {sep} "
    return f"{numero_str}{sep}{ano_str}"

def gerar_documentos():
    folder = "teste"
    os.makedirs(folder, exist_ok=True)
    om_list = ["OM Exército", "OM Marinha", "OM Aeronáutica", "OM Polícia", "OM Fuzileiros"]
    for i in range(1, 6):
        data = {"OS": [], "OM": [], "VALOR": []}
        for _ in range(100):
            data["OS"].append(generate_random_os())
            data["OM"].append(random.choice(om_list))
            data["VALOR"].append(random.randint(1000, 20000))
        df = pd.DataFrame(data)
        df.to_excel(os.path.join(folder, f"tabela {i}.xlsx"), index=False)
    QMessageBox.information(None, "Sucesso", "Documentos gerados com sucesso.")

def pad_left(value, width):
    return str(value).zfill(width)

def standardize_os(os_str):
    os_str = os_str.strip()
    match = re.search(r"(\d+)\D+(\d+)", os_str)
    if match:
        num, ano = match.groups()
        # Se ano for "25" ou "24", converte para "2025" ou "2024", respectivamente; 
        # caso contrário, preenche com zeros à esquerda para ter 4 dígitos.
        if ano == "25":
            ano = "2025"
        elif ano == "24":
            ano = "2024"
        else:
            ano = ano.zfill(4)
        return f"{pad_left(num, 5)}/{ano}"
    return os_str

def tratar_dados():
    source_folder = "teste"
    target_folder = "relatorio"
    os.makedirs(target_folder, exist_ok=True)
    all_dfs = []
    for file in glob.glob(os.path.join(source_folder, "tabela *.xlsx")):
        df = pd.read_excel(file)
        df["OS"] = df["OS"].apply(standardize_os)
        all_dfs.append(df)
    if all_dfs:
        consolidated = pd.concat(all_dfs, ignore_index=True)
        consolidated.to_excel(os.path.join(target_folder, "relatorio.xlsx"), index=False)
        QMessageBox.information(None, "Sucesso", "Dados tratados e relatório criado com sucesso.")
    else:
        QMessageBox.warning(None, "Atenção", "Nenhum arquivo encontrado na pasta teste.")

def add_button_func(text, slot, layout, tooltip=None, button_size=None):
    button = QPushButton(text)
    if button_size:
        button.setFixedSize(QSize(*button_size))
    button.setStyleSheet("""
        QPushButton {
            background-color: #1E1E2E;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #CCCCCC;
            padding: 0px 16px;
            border-radius: 5px;
        }
        QPushButton:hover { background-color: #A17B00; }
        QPushButton:pressed { background-color: #252536; }
    """)
    if tooltip:
        button.setToolTip(tooltip)
    button.clicked.connect(slot)
    layout.addWidget(button)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button

def create_excel_layout(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    title_layout = QHBoxLayout()
    title_label = QLabel(title_text)
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)

    add_button_func("Gerar Documentos", gerar_documentos, title_layout, tooltip="Gerar planilhas")
    add_button_func("Tratar Dados", tratar_dados, title_layout, tooltip="Consolidar dados")
    
    main_layout.addLayout(title_layout)
    return main_frame