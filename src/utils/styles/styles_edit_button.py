def apply_edit_dialog_style(dialog):
    """Aplica o estilo ao QDialog e seus componentes."""
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1E2E;
            color: #FFFFFF;
            font-size: 16px;

        }
        QLabel {
            color: #FFFFFF;
            font-size: 16px;
            
        }
        QLineEdit {
            background-color: #FFFFFF;
            font-size: 16px;            
        }            
        QTabWidget::pane {
            border: 1px solid #3D3D5C;
            background-color: #2D2D44;
            border-radius: 5px;
            font-size: 14px; 
        }
        QTabBar::tab {
            background-color: #2D2D44;
            color: #FFFFFF;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-size: 14px; 
        }
        QTabBar::tab:selected {
            background-color: #3D3D5C;
            font-weight: bold;
        }
        QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            font-size: 16px;
        }
        QPushButton {
            background-color: #3CB500;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #60DE65;
        }
        QPushButton:pressed {
            background-color: #60DE65;
        }
        QPushButton[text="Cancelar"] {
            background-color: #f44336;
        }
        QPushButton[text="Cancelar"]:hover {
            background-color: #F56E6E;
        }
    """)
