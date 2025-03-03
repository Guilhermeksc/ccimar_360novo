from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton, QLineEdit
from utils.gerenciamento_pastas import open_folder, open_template, criar_pasta, criar_pasta_e_docx, criar_pasta_e_pdf
from paths import TEMPLATE_TEST2_PATH

def create_content_nota_auditoria_test2(title_text):
    """Creates a content layout with a title and two buttons."""
    content_frame = QFrame()
    content_frame.setStyleSheet("""
        background-color: #44475A; 
        border-radius: 8px; 
        padding: 10px;
    """)
    layout = QVBoxLayout(content_frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(15)

    # Title
    title = QLabel(title_text)
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF")
    layout.addWidget(title)

    # Input Fields
    pasta_input = QLineEdit()
    pasta_input.setPlaceholderText("Nome da Pasta")
    layout.addWidget(pasta_input)

    setor_input = QLineEdit()
    setor_input.setPlaceholderText("Setor Responsável")
    layout.addWidget(setor_input)

    natalia_input = QLineEdit()
    natalia_input.setPlaceholderText("Natalia")
    layout.addWidget(natalia_input)

    # Buttons
    btn_open_folder = QPushButton("Abrir Pasta")
    btn_open_folder.setStyleSheet("background-color: #6272A4; color: white; padding: 8px; border-radius: 4px;")
    btn_open_folder.clicked.connect(lambda: open_folder(pasta_input.text()))

    btn_open_template = QPushButton("Abrir Template")
    btn_open_template.setStyleSheet("background-color: #8BE9FD; color: black; padding: 8px; border-radius: 4px;")
    btn_open_template.clicked.connect(lambda: open_template())

    btn_create_folder = QPushButton("Criar Pasta")
    btn_create_folder.setStyleSheet("background-color: #50FA7B; color: black; padding: 8px; border-radius: 4px;")
    btn_create_folder.clicked.connect(lambda: criar_pasta(pasta_input.text()))

    btn_create_docx = QPushButton("Criar Pasta e Arquivo DOCX")
    btn_create_docx.setStyleSheet("background-color: #FFB86C; color: black; padding: 8px; border-radius: 4px;")
    btn_create_docx.clicked.connect(lambda: criar_pasta_e_docx(pasta_input.text(), TEMPLATE_TEST2_PATH, setor_input.text(), natalia_input.text()))

    btn_create_pdf = QPushButton("Criar Pasta e Arquivo PDF")
    btn_create_pdf.setStyleSheet("background-color: #FF5555; color: white; padding: 8px; border-radius: 4px;")
    btn_create_pdf.clicked.connect(lambda: criar_pasta_e_pdf(pasta_input.text()))

    # Add buttons to layout
    layout.addWidget(btn_open_folder)
    layout.addWidget(btn_open_template)
    layout.addWidget(btn_create_folder)
    layout.addWidget(btn_create_docx)
    layout.addWidget(btn_create_pdf)

    return content_frame
