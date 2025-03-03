import os
import json
import pandas as pd
from PyQt6.QtWidgets import (
    QTableView, QMessageBox, QStyledItemDelegate,
)
from PyQt6.QtCore import Qt
from paths import OM_REPRESENTATIVAS_PATH

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

def load_config():
    if os.path.exists(OM_REPRESENTATIVAS_PATH):
        try:
            with open(OM_REPRESENTATIVAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao carregar a configuração: {e}")
            return None
    else:
        default_config = {
            "mapa_om_representativas": []
        }
        try:
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao criar arquivo de configuração: {e}")
        return default_config

class ExcelModelManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.required_sheet = "Mapa OM Representativas"
        self.required_cols = ["Critério", "Descrição", "Percentual", "Parâmetro", "Pontos", "Peso"]

    def validate(self) -> bool:
        try:
            sheets = pd.read_excel(self.file_path, sheet_name=None)
        except Exception as e:
            self._show_message(f"Erro ao ler o arquivo: {e}")
            return False

        if self.required_sheet not in sheets:
            self._show_message(f"Aba ausente: {self.required_sheet}")
            return False

        df = sheets[self.required_sheet]
        missing_cols = [col for col in self.required_cols if col not in df.columns]
        if missing_cols:
            self._show_message("Colunas ausentes: " + ", ".join(missing_cols))
            return False

        return True

    def _show_message(self, message: str):
        QMessageBox.critical(None, "Erro na Importação", message)
