import os
import json
import pandas as pd
from PyQt6.QtWidgets import (
    QTableView, QMessageBox, QStyledItemDelegate,
)
from PyQt6.QtCore import Qt
from paths import CONFIG_PAINT_PATH

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
    if os.path.exists(CONFIG_PAINT_PATH):
        try:
            with open(CONFIG_PAINT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao carregar a configuração: {e}")
            return None
    else:
        default_config = {
            "objetos_auditaveis": [],
            "multiplicador": {"materialidade": 0, "relevancia": 0, "criticidade": 0},
            "pontuacao_criterios": {"materialidade": [], "relevancia": [], "criticidade": []}
        }
        try:
            with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao criar arquivo de configuração: {e}")
        return default_config

class ExcelModelManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.required_sheets = ["Compilado", "Materialidade", "Relevância", "Criticidade"]
        self.required_cols_compilado = ["NR", "Objetos Auditáveis"]
        self.required_cols_others = ["Critério", "Tipo", "Descrição", "Pontuação"]

    def validate(self) -> bool:
        try:
            sheets = pd.read_excel(self.file_path, sheet_name=None)
        except Exception as e:
            self._show_message(f"Erro ao ler o arquivo: {e}")
            return False

        missing_sheets = [s for s in self.required_sheets if s not in sheets]
        if missing_sheets:
            self._show_message("Abas ausentes: " + ", ".join(missing_sheets))
            return False

        errors = []
        compilado = sheets["Compilado"]
        missing_cols_comp = [c for c in self.required_cols_compilado if c not in compilado.columns]
        if missing_cols_comp:
            errors.append("Compilado: " + ", ".join(missing_cols_comp))

        for aba in ["Materialidade", "Relevância", "Criticidade"]:
            df = sheets[aba]
            missing_cols = [c for c in self.required_cols_others if c not in df.columns]
            if missing_cols:
                errors.append(f"{aba}: " + ", ".join(missing_cols))

        if errors:
            self._show_message("Colunas ausentes:\n" + "\n".join(errors))
            return False

        return True

    def _show_message(self, message: str):
        QMessageBox.critical(None, "Erro na Importação", message)
