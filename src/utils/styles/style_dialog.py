def apply_dialog_style(dialog):
    """Aplica o estilo ao QDialog e seus componentes."""
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1E2E;
            color: #FFFFFF;
            border-radius: 8px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
        }
        QSpinBox {
            background-color: #FFFFFF;
            font-size: 14px;
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
        QPushButton[text="Cancelar"] {
            background-color: #f44336;
        }
        QPushButton[text="Cancelar"]:hover {
            background-color: #e53935;
        }
        QPushButton[text="Cancelar"]:pressed {
            background-color: #d32f2f;
        }
    """)
