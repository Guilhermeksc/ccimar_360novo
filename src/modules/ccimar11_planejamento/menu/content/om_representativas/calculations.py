import os
import json
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QDialog, QDialogButtonBox,
    QSpinBox, QFormLayout
)
from paths import OM_REPRESENTATIVAS_PATH
from .tableview import load_config
from PyQt6.QtCore import QTimer

class MultiplicadoresDialog(QDialog):
    def __init__(self, update_callback=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Multiplicadores")
        self.setMinimumSize(300, 200)
        self.update_callback = update_callback

        self.setStyleSheet("""
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

        layout = QVBoxLayout(self)
        self.config = load_config() or {}
        self.spinboxes = {}  # mapeia cada critério ao respectivo QSpinBox

        form_layout = QFormLayout()
        if "mapa_om_representativas" in self.config:
            for item in self.config["mapa_om_representativas"]:
                criterio = item.get("Critério", "")
                peso = item.get("Peso", 0)
                spinbox = QSpinBox()
                spinbox.setMinimum(0)
                spinbox.setMaximum(1000)
                spinbox.setValue(peso)
                self.spinboxes[criterio] = spinbox
                form_layout.addRow(criterio, spinbox)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("Salvar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.save_multiplicadores)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_multiplicadores(self):
        config = load_config() or {}
        if "mapa_om_representativas" not in config:
            QMessageBox.critical(self, "Erro", "Configuração inválida.")
            return

        # Atualiza o valor de "Peso" para cada critério conforme o spinbox
        for item in config["mapa_om_representativas"]:
            criterio = item.get("Critério", "")
            if criterio in self.spinboxes:
                item["Peso"] = self.spinboxes[criterio].value()

        try:
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Sucesso")
            msg_box.setText("Multiplicadores atualizados com sucesso!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1E1E2E;
                    color: white;
                    font-size: 14px;
                    border-radius: 8px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            QTimer.singleShot(1000, msg_box.accept)
            msg_box.exec()

            # Atualiza o table_view via callback, se informado
            if self.update_callback:
                self.update_callback()

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar no JSON: {e}")
