def apply_edit_dialog_style(dialog):
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
        QTabWidget::pane {
            border: 1px solid #3D3D5C;
            background-color: #2D2D44;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #3D3D5C;
            color: #FFFFFF;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #5D5D8C;
            font-weight: bold;
        }
        QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            padding: 5px;
            border-radius: 3px;
            min-height: 25px;
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
