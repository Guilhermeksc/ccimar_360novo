import os
import json
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QDialog, QDialogButtonBox,
    QSpinBox
)
from paths import CONFIG_PAINT_PATH
from .tableview import load_config
from PyQt6.QtCore import QTimer
from utils.styles.style_dialog import apply_dialog_style

class MultiplicadoresDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Multiplicadores")
        self.setMinimumSize(300, 200)

        apply_dialog_style(self)

        # Layout principal
        layout = QVBoxLayout(self)
        self.inputs = {}

        # Carregar os multiplicadores do JSON
        config = load_config()
        multiplicadores = config.get("multiplicador", {
            "materialidade": 4,
            "relevancia": 2,
            "criticidade": 4
        })

        # Criar campos para editar os multiplicadores
        for key, label_text in [("materialidade", "Materialidade"), ("relevancia", "Relevância"), ("criticidade", "Criticidade")]:
            hbox = QHBoxLayout()
            label = QLabel(f"{label_text}:")
            spinbox = QSpinBox()
            spinbox.setRange(1, 10)  # Intervalo permitido
            spinbox.setValue(multiplicadores.get(key, 4))
            spinbox.setMinimumWidth(60)
            hbox.addWidget(label)
            hbox.addWidget(spinbox)
            layout.addLayout(hbox)
            self.inputs[key] = spinbox

        # Botões de ação
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("Salvar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.save_multiplicadores)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


    def save_multiplicadores(self):
        """ Salva os multiplicadores no JSON e atualiza a interface """
        config = load_config()
        if not config:
            QMessageBox.critical(self, "Erro", "Falha ao carregar a configuração.")
            return

        # Atualizar os multiplicadores
        config["multiplicador"] = {
            "materialidade": self.inputs["materialidade"].value(),
            "relevancia": self.inputs["relevancia"].value(),
            "criticidade": self.inputs["criticidade"].value()
        }

        # Salvar no arquivo JSON
        try:
            with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            # Criar a QMessageBox personalizada
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Sucesso")
            msg_box.setText("Multiplicadores atualizados com sucesso!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            # Aplicar o CSS para manter o tema escuro
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

            msg_box.exec()  # Exibir a mensagem

            self.accept()  # Fecha o diálogo após salvar
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar no JSON: {e}")


