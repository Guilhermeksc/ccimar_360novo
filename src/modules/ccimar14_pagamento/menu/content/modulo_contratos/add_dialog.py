import json
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QMessageBox, QWidget,
    QDialog, QComboBox, QFormLayout, QDialogButtonBox,
    QLineEdit, QTextEdit, QDateEdit
)

from paths import CADASTRO_OBJETOS_AUDITAVEIS_PATH
from .tableview import load_config
from utils.styles.styles_add_dialog import apply_add_dialog_style

def get_next_nr():
    config = load_config() or {"objetos_auditaveis": []}
    if config["objetos_auditaveis"]:
        max_nr = max(int(item.get("nr", 0)) for item in config["objetos_auditaveis"])
    else:
        max_nr = 0
    return str(max_nr + 1)

def save_new_entry(entry, parent=None):
    config = load_config() or {"objetos_auditaveis": []}
    config["objetos_auditaveis"].append(entry)
    try:
        with open(CADASTRO_OBJETOS_AUDITAVEIS_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        QMessageBox.information(parent, "Sucesso", "Novo registro adicionado com sucesso!")
    except Exception as e:
        QMessageBox.critical(parent, "Erro", f"Falha ao salvar a configuração: {e}")

class AddAuditavelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Novo Objeto Auditável")
        self._init_ui()
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Estilo para o diálogo
        apply_add_dialog_style(self)
        
    def _init_ui(self):
        form = QFormLayout(self)

        # Tipo de Serviço (ComboBox editável)
        self.tipo_cb = QComboBox()
        self.tipo_cb.setEditable(True)
        self.tipo_cb.addItems(["Avaliação", "Consultoria", "Apuração"])
        form.addRow("Tipo de Serviço:", self.tipo_cb)

        # Descrição (QTextEdit)
        self.descricao_te = QTextEdit()
        form.addRow("Descrição:", self.descricao_te)

        # Objetivo da Auditoria (QTextEdit maior)
        self.objetivo_te = QTextEdit()
        self.objetivo_te.setFixedHeight(80)
        form.addRow("Objetivo Auditoria:", self.objetivo_te)

        # Origem da Demanda (ComboBox editável)
        self.origem_cb = QComboBox()
        self.origem_cb.setEditable(True)
        self.origem_cb.addItems(["Solicitação da Gestão", "Obrigação Legal", "Avaliação de Riscos"])
        form.addRow("Origem Demanda:", self.origem_cb)

        # Início (DateEdit)
        self.inicio_de = QDateEdit()
        self.inicio_de.setCalendarPopup(True)
        form.addRow("Início:", self.inicio_de)

        # Conclusão (DateEdit)
        self.conclusao_de = QDateEdit()
        self.conclusao_de.setCalendarPopup(True)
        form.addRow("Conclusão:", self.conclusao_de)

        # HH (LineEdit)
        self.hh_le = QLineEdit()
        form.addRow("HH:", self.hh_le)

        # Situação (ComboBox)
        self.situacao_cb = QComboBox()
        self.situacao_cb.addItems(["Planejamento", "Previsto", "Concluído"])
        form.addRow("Situação:", self.situacao_cb)

        # Observações (estrutura dinâmica)
        self.obs_widget = QWidget()
        self.obs_layout = QVBoxLayout(self.obs_widget)
        self.obs_list = []
        btn_add_obs = QPushButton("Adicionar Observação")
        btn_add_obs.clicked.connect(self.add_obs)
        form.addRow("Observações:", btn_add_obs)
        form.addRow("", self.obs_widget)

        # Botões OK/Cancelar
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        form.addRow(btn_box)

    def add_obs(self):
        obs_line = QLineEdit()
        self.obs_layout.addWidget(obs_line)
        self.obs_list.append(obs_line)

    def get_data(self):
        return {
            "nr": get_next_nr(),
            "tipo_de_servico": self.tipo_cb.currentText(),
            "descricao": self.descricao_te.toPlainText(),
            "objetivo_auditoria": self.objetivo_te.toPlainText(),
            "origem_demanda": self.origem_cb.currentText(),
            "inicio": self.inicio_de.date().toString("yyyy-MM-dd"),
            "conclusao": self.conclusao_de.date().toString("yyyy-MM-dd"),
            "hh": self.hh_le.text(),
            "situacao": self.situacao_cb.currentText(),
            "observacoes": [obs.text() for obs in self.obs_list if obs.text().strip()]
        }
