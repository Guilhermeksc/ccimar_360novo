import os
import json
import subprocess
import pandas as pd
from PyQt6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QDialog, QStyledItemDelegate
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt
from utils.styles.style_table import apply_table_style
from utils.styles.style_add_button import add_button_func
from pathlib import Path
from paths import (
    update_dir, save_config, get_config_value,
    DEFAULT_DATABASE_DIR, DEFAULT_JSON_DIR, DEFAULT_TEMPLATE_DIR, reload_paths,
    AGENTES_RESPONSAVEIS_FILE
)
def create_local_salvamento(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Criando e adicionando o widget AgentesResponsaveisWidget
    local_salvamento_widget = AlterarLocalSalvamentoWidget(icons)
    main_layout.addWidget(local_salvamento_widget)
    
    return main_frame

class CenteredDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class CustomTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)
        self.setItemDelegate(CenteredDelegate(self))
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                model = self.model()
                check_item = model.item(index.row(), 0)
                if check_item and check_item.isCheckable():
                    new_state = Qt.CheckState.Unchecked if check_item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
                    check_item.setCheckState(new_state)
        super().mousePressEvent(event)

class AlterarLocalSalvamentoWidget(QWidget):
    def __init__(self, icons, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Alterar Diretórios Base")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_label)
        layout.addStretch()

        # Ler os valores atualizados do arquivo de configuração
        db_config = get_config_value("DATABASE_DIR", str(DEFAULT_DATABASE_DIR))
        json_config = get_config_value("JSON_DIR", str(DEFAULT_JSON_DIR))
        template_config = get_config_value("TEMPLATE_DIR", str(DEFAULT_TEMPLATE_DIR))
        print("Carregando DATABASE_DIR:", db_config)
        print("Carregando JSON_DIR:", json_config)
        print("Carregando TEMPLATE_DIR:", template_config)

        # Linha para DATABASE_DIR
        self.db_label = QLabel(f"DATABASE_DIR: {db_config}")
        self.db_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")

        db_layout = QVBoxLayout()
        db_layout.addWidget(self.db_label)

        btn_db = add_button_func(
            "Alterar DATABASE_DIR", 
            "export", 
            self.alterar_database_dir, 
            db_layout, 
            self.icons, 
            tooltip="Alterar o diretório padrão de DATABASE_DIR", 
            button_size=(250, 40)
        )

        # Linha para JSON_DIR
        self.json_label = QLabel(f"JSON_DIR: {json_config}")
        self.json_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")

        json_layout = QVBoxLayout()
        json_layout.addWidget(self.json_label)
        btn_json = add_button_func(
            "Alterar JSON_DIR", 
            "export", 
            self.alterar_json_dir, 
            json_layout, 
            self.icons, 
            tooltip="Alterar o diretório padrão de JSON_DIR", 
            button_size=(250, 40) 
        )

        # Linha para JSON_DIR
        self.template_label = QLabel(f"TEMPLATE_DIR: {template_config}")
        self.template_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")

        template_layout = QVBoxLayout()
        template_layout.addWidget(self.template_label)
        btn_template = add_button_func(
            "Alterar TEMPLATE_DIR", 
            "export", 
            self.alterar_template_dir, 
            template_layout, 
            self.icons, 
            tooltip="Alterar o diretório padrão de JSON_DIR", 
            button_size=(250, 40) 
        )

        layout.addLayout(db_layout)
        layout.addLayout(json_layout)
        layout.addLayout(template_layout)
        layout.addStretch()
        self.setLayout(layout)

    def alterar_database_dir(self):
        # Utiliza o valor atual lido do arquivo de configuração
        new_db = update_dir("Selecione o novo diretório para DATABASE_DIR", "DATABASE_DIR", Path(get_config_value("DATABASE_DIR", str(DEFAULT_DATABASE_DIR))), self)
        if new_db:
            save_config("DATABASE_DIR", str(new_db))
            # Após salvar, recarrega os caminhos
            reload_paths()
            self.db_label.setText(f"DATABASE_DIR: {str(new_db)}")
            print("Novo DATABASE_DIR definido:", new_db)
            # Atualiza automaticamente o JSON_DIR como padrão derivado
            new_json = new_db / "json"
            save_config("JSON_DIR", str(new_json))
            reload_paths()
            self.json_label.setText(f"JSON_DIR: {str(new_json)}")
            print("Novo JSON_DIR derivado:", new_json)

    def alterar_json_dir(self):
        new_json = update_dir("Selecione o novo diretório para JSON_DIR", "JSON_DIR", Path(get_config_value("JSON_DIR", str(DEFAULT_JSON_DIR))), self)
        if new_json:
            save_config("JSON_DIR", str(new_json))
            reload_paths()
            self.json_label.setText(f"JSON_DIR: {str(new_json)}")
            print("Novo JSON_DIR definido:", new_json)

    def alterar_template_dir(self):
        new_json = update_dir("Selecione o novo diretório para TEMPLATE_DIR", "TEMPLATE_DIR", Path(get_config_value("TEMPLATE_DIR", str(DEFAULT_TEMPLATE_DIR))), self)
        if new_json:
            save_config("TEMPLATE_DIR", str(new_json))
            reload_paths()
            self.template_label.setText(f"TEMPLATE_DIR: {str(new_json)}")
            print("Novo TEMPLATE_DIR definido:", new_json)
