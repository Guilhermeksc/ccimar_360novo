def apply_add_dialog_style(dialog):
    """Aplica o estilo ao QDialog e seus componentes."""
    dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E2E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #000000;
            }                         
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton[text="Cancel"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #e53935;
            }
    """)
