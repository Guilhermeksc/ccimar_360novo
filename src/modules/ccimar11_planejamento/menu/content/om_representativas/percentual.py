from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLabel, QDoubleSpinBox, QDialogButtonBox, QMessageBox
)
import json
from paths import OM_REPRESENTATIVAS_PATH
from .tableview import load_config

class PercentualDialog(QDialog):
    def __init__(self, update_callback=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Percentuais")
        self.setMinimumSize(400, 300)
        self.update_callback = update_callback

        self.config = load_config() or {}
        self.spinboxes = {}      # { critério: [(índice, spinbox), ...] }
        self.total_labels = {}   # { critério: QLabel }

        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Cria uma aba para cada grupo de critério
        if "mapa_om_representativas" in self.config:
            for group in self.config["mapa_om_representativas"]:
                criterio = group.get("Critério", "")
                itens = group.get("itens", [])
                self.spinboxes[criterio] = []
                
                tab = QWidget()
                form_layout = QFormLayout(tab)

                # Para cada item, cria um QDoubleSpinBox (valores exibidos em porcentagem)
                for i, item in enumerate(itens):
                    descricao = item.get("Descrição", "")
                    percentual = item.get("Percentual", 0.0)
                    percentage_value = int(percentual * 100)
                    spinbox = QDoubleSpinBox()
                    spinbox.setSuffix("%")
                    spinbox.setDecimals(0)
                    spinbox.setMinimum(0)
                    spinbox.setMaximum(100)
                    spinbox.setValue(percentage_value)
                    self.spinboxes[criterio].append((i, spinbox))
                    form_layout.addRow(descricao, spinbox)
                    # Conecta para atualizar o total sempre que o valor mudar
                    spinbox.valueChanged.connect(lambda val, cr=criterio: self.update_total(cr))
                
                # Exibe o total da soma dos percentuais para o critério
                total_label = QLabel()
                form_layout.addRow("Total:", total_label)
                self.total_labels[criterio] = total_label
                self.update_total(criterio)

                self.tab_widget.addTab(tab, criterio)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("Salvar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.save_percentuais)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_total(self, criterio):
        total = sum(spinbox.value() for _, spinbox in self.spinboxes[criterio])
        self.total_labels[criterio].setText(f"{total}%")

    def save_percentuais(self):
        # Verifica se o somatório de cada critério é exatamente 100%
        for group in self.config.get("mapa_om_representativas", []):
            criterio = group.get("Critério", "")
            total = sum(spinbox.value() for _, spinbox in self.spinboxes.get(criterio, []))
            if total != 100:
                QMessageBox.critical(self, "Erro",
                    f"O total do percentual para '{criterio}' deve ser 100%, mas é {total}%.")
                return

        # Atualiza os percentuais na configuração
        for group in self.config.get("mapa_om_representativas", []):
            criterio = group.get("Critério", "")
            for (i, spinbox) in self.spinboxes.get(criterio, []):
                # Salva o valor como fração
                group["itens"][i]["Percentual"] = spinbox.value() / 100.0

        try:
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Sucesso", "Percentuais atualizados com sucesso!")
            if self.update_callback:
                self.update_callback()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar no JSON: {e}")
