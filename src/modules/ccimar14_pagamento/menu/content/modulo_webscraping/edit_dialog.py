from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QDialog, 
    QComboBox, QFormLayout, QTabWidget, QDialogButtonBox,
    QWidget, QTextEdit, QLineEdit, QPushButton, QDateEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from utils.styles.styles_edit_button import apply_edit_dialog_style
from paths import CADASTRO_OBJETOS_AUDITAVEIS_PATH
import json

class EditDialog(QDialog):
    def __init__(self, parent=None, objeto_auditavel=None, config=None, row_index=None):
        super().__init__(parent)
        self.objeto_auditavel = objeto_auditavel
        self.config = config
        self.row_index = row_index
        self.deleted = False  # Flag para indicar que o objeto foi excluído

        self.setWindowTitle(f"Editar Objeto Auditável: {objeto_auditavel.get('descricao', '')}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        apply_edit_dialog_style(self)  # Aplica o estilo personalizado

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Informações básicas (somente leitura) com botão "Excluir Objeto"
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #2D2D44; border-radius: 5px; padding: 10px;")
        info_layout = QHBoxLayout(info_frame)
        self.nr_label = QLabel(f"<b>NR:</b> {objeto_auditavel.get('nr', '')}")
        self.nr_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.nr_label)
        self.desc_label = QLabel(f"<b>Descrição:</b> {objeto_auditavel.get('descricao', '')}")
        self.desc_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.desc_label)
        info_layout.addStretch()  # Empurra os widgets seguintes para a direita

        # Botão discreto "Excluir Objeto"
        self.btn_excluir = QPushButton("Excluir Objeto")
        self.btn_excluir.setStyleSheet("background: none; color: #f44336; border: none;")
        self.btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_excluir.clicked.connect(self.excluir_objeto)
        info_layout.addWidget(self.btn_excluir)

        main_layout.addWidget(info_frame)

        # Cria as abas
        tab_widget = QTabWidget()

        # Aba "Informações"
        informacoes_tab = QWidget()
        informacoes_layout = QFormLayout(informacoes_tab)
        informacoes_layout.setContentsMargins(15, 15, 15, 15)
        informacoes_layout.setSpacing(10)
        tab_widget.addTab(informacoes_tab, "Informações")

        # Aba "Homem-hora"
        homem_hora_tab = QWidget()
        homem_hora_layout = QFormLayout(homem_hora_tab)
        homem_hora_layout.setContentsMargins(15, 15, 15, 15)
        homem_hora_layout.setSpacing(10)
        tab_widget.addTab(homem_hora_tab, "Homem-hora")

        main_layout.addWidget(tab_widget)

        # Campos da aba "Informações"
        self.tipo_cb = QComboBox()
        self.tipo_cb.setEditable(True)
        self.tipo_cb.addItems(["Avaliação", "Consultoria", "Apuração"])
        self.tipo_cb.setCurrentText(objeto_auditavel.get("tipo_de_servico", ""))
        informacoes_layout.addRow("Tipo de Serviço:", self.tipo_cb)

        self.descricao_te = QTextEdit()
        self.descricao_te.setPlainText(objeto_auditavel.get("descricao", ""))
        informacoes_layout.addRow("Descrição:", self.descricao_te)

        self.objetivo_te = QTextEdit()
        self.objetivo_te.setFixedHeight(80)
        self.objetivo_te.setPlainText(objeto_auditavel.get("objetivo_auditoria", ""))
        informacoes_layout.addRow("Objetivo Auditoria:", self.objetivo_te)

        self.origem_cb = QComboBox()
        self.origem_cb.setEditable(True)
        self.origem_cb.addItems(["Solicitação da Gestão", "Obrigação Legal", "Avaliação de Riscos"])
        self.origem_cb.setCurrentText(objeto_auditavel.get("origem_demanda", ""))
        informacoes_layout.addRow("Origem Demanda:", self.origem_cb)

        self.inicio_de = QDateEdit()
        self.inicio_de.setCalendarPopup(True)
        inicio_str = objeto_auditavel.get("inicio", "")
        if inicio_str:
            date_inicio = QDate.fromString(inicio_str, "yyyy-MM-dd")
            if date_inicio.isValid():
                self.inicio_de.setDate(date_inicio)
        informacoes_layout.addRow("Início:", self.inicio_de)

        self.conclusao_de = QDateEdit()
        self.conclusao_de.setCalendarPopup(True)
        conclusao_str = objeto_auditavel.get("conclusao", "")
        if conclusao_str:
            date_conclusao = QDate.fromString(conclusao_str, "yyyy-MM-dd")
            if date_conclusao.isValid():
                self.conclusao_de.setDate(date_conclusao)
        informacoes_layout.addRow("Conclusão:", self.conclusao_de)

        self.situacao_cb = QComboBox()
        self.situacao_cb.addItems(["Planejamento", "Previsto", "Concluído"])
        self.situacao_cb.setCurrentText(objeto_auditavel.get("situacao", ""))
        informacoes_layout.addRow("Situação:", self.situacao_cb)

        # Observações dinâmicas
        self.obs_widget = QWidget()
        self.obs_layout = QVBoxLayout(self.obs_widget)
        self.obs_list = []
        observacoes = objeto_auditavel.get("observacoes", [])
        if isinstance(observacoes, str):
            observacoes = [observacoes] if observacoes else []
        for obs in observacoes:
            obs_line = QLineEdit(obs)
            self.obs_layout.addWidget(obs_line)
            self.obs_list.append(obs_line)
        btn_add_obs = QPushButton("Adicionar Observação")
        btn_add_obs.clicked.connect(self.add_obs)
        informacoes_layout.addRow("Observações:", btn_add_obs)
        informacoes_layout.addRow("", self.obs_widget)

        # Campo da aba "Homem-hora"
        self.hh_le = QLineEdit()
        self.hh_le.setText(objeto_auditavel.get("hh", ""))
        homem_hora_layout.addRow("HH:", self.hh_le)

        # Botões OK e Cancelar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Salvar")
        ok_button.setMinimumWidth(100)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancelar")
        cancel_button.setStyleSheet("background-color: #f44336;")
        cancel_button.setMinimumWidth(100)
        main_layout.addWidget(button_box, 0, Qt.AlignmentFlag.AlignRight)

    def add_obs(self):
        obs_line = QLineEdit()
        self.obs_layout.addWidget(obs_line)
        self.obs_list.append(obs_line)

    def get_updated_data(self):
        return {
            "nr": self.objeto_auditavel.get("nr", ""),
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
