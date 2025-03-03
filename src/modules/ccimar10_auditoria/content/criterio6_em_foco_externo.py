from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QPushButton
from utils.gerenciamento_pastas import open_folder, open_template

def create_criterio6_foco_externo(title_text):
    """Creates a content layout with a title and two buttons."""
    content_frame = QFrame()
    content_frame.setStyleSheet("""
            QFrame { 
                padding: 5px;
            }
        """)

    layout = QVBoxLayout(content_frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(15)

    # Title
    title = QLabel(title_text)
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF")
    layout.addWidget(title)

    # Buttons
    btn_open_folder = QPushButton("Abrir Pasta")
    btn_open_folder.setStyleSheet("background-color: #6272A4; color: white; padding: 8px; border-radius: 4px;")
    btn_open_folder.clicked.connect(lambda: open_folder())

    btn_open_template = QPushButton("Abrir Template")
    btn_open_template.setStyleSheet("background-color: #8BE9FD; color: black; padding: 8px; border-radius: 4px;")
    btn_open_template.clicked.connect(lambda: open_template())

    layout.addWidget(btn_open_folder)
    layout.addWidget(btn_open_template)

    return content_frame