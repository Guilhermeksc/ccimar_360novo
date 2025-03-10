import pandas as pd
from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QMessageBox

def create_criterios_pesos(title_text, database_model):
    """Cria a página inicial do programa PAINT com título, descrição e botões de ação."""
    # Criação do frame com estilo
    content_frame = QFrame()
    content_frame.setStyleSheet("""
        QFrame {
            padding: 10px;
            background-color: #44475A;
            border-radius: 8px;
        }
    """)

    # Configuração do layout
    layout = QVBoxLayout(content_frame)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # Título da página
    title = QLabel("Plano Anual de Auditoria Interna (PAINT)")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    layout.addWidget(title)

    # Descrição breve extraída do contexto do PAINT
    description = QLabel("Programa destinado a padronizar e otimizar os procedimentos de auditoria interna, "
                         "seguindo critérios e pesos conforme definido nos manuais.")
    description.setStyleSheet("font-size: 14px; color: #FFFFFF;")
    description.setWordWrap(True)
    layout.addWidget(description)

    # # Botões de ações principais
    # btn_import = QPushButton("Importar Dados")
    # btn_print = QPushButton("Imprimir")
    # btn_save = QPushButton("Salvar")
    
    # layout.addWidget(btn_import)
    # layout.addWidget(btn_print)
    # layout.addWidget(btn_save)

    return content_frame
