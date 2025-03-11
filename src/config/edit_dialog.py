from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from paths import *
from utils.styles.styles_edit_button import apply_edit_dialog_style

class EditDialog(QDialog):
    def __init__(self, data, icons, categoria="geral", parent=None):
        super().__init__(parent)
        self.icons = icons
        self.categoria = categoria
        self.setFixedSize(500, 450)
        self.setWindowIcon(self.icons["edit"])
        apply_edit_dialog_style(self)
        self.setWindowTitle("Editar Responsáveis")
        self.setup_ui(data)

    def setup_ui(self, data):
        layout = QVBoxLayout(self)

        # Nome
        layout.addWidget(QLabel("Nome:"))
        self.nome_input = QLineEdit(data.get("Nome", ""))
        self.nome_input.setPlaceholderText("Digite o nome")
        self.nome_input.textChanged.connect(self.forcar_caixa_alta)
        layout.addWidget(self.nome_input)

        # Nome de Guerra
        layout.addWidget(QLabel("Nome de Guerra:"))
        self.nome_guerra_input = QLineEdit(data.get("Nome de Guerra", ""))
        self.nome_guerra_input.setPlaceholderText("Digite o nome de guerra")
        layout.addWidget(self.nome_guerra_input)

        # Posto
        layout.addWidget(QLabel("Posto:"))
        self.posto_input = QComboBox()
        self.posto_input.setEditable(True)
        self.posto_input.currentTextChanged.connect(self.atualizar_abreviacao)
        layout.addWidget(self.posto_input)

        # Abreviação do Posto
        layout.addWidget(QLabel("Abreviação do Posto:"))
        self.abrev_posto_input = QComboBox()
        self.abrev_posto_input.setEditable(True)
        layout.addWidget(self.abrev_posto_input)

        # Preencher os ComboBox
        self.atualizar_posto()
        self.posto_input.setCurrentText(data.get("Posto", ""))
        self.atualizar_abreviacao(self.posto_input.currentText())
        self.abrev_posto_input.setCurrentText(data.get("Abreviação", ""))

        # NIP
        layout.addWidget(QLabel("NIP:"))
        self.nip_input = QLineEdit(data.get("NIP", ""))
        self.nip_input.setPlaceholderText("Digite o NIP")
        layout.addWidget(self.nip_input)

        # Função
        layout.addWidget(QLabel("Função:"))
        self.funcao_input = QComboBox()
        self.funcao_input.setEditable(True)
        self.inicializar_funcoes()
        self.funcao_input.setCurrentText(data.get("Função", ""))
        layout.addWidget(self.funcao_input)

        # Botões de confirmação
        button_box = QDialogButtonBox()
        salvar_button = QPushButton("Salvar")
        cancelar_button = QPushButton("Cancelar")
        button_box.addButton(salvar_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancelar_button, QDialogButtonBox.ButtonRole.RejectRole)
        button_box.setCursor(Qt.CursorShape.PointingHandCursor) 
        salvar_button.clicked.connect(self.accept)
        cancelar_button.clicked.connect(self.reject)
        layout.addWidget(button_box)


    def forcar_caixa_alta(self, text):
        self.nome_input.blockSignals(True)
        self.nome_input.setText(text.upper())
        self.nome_input.blockSignals(False)

    def atualizar_posto(self):
        postos_ord = [
            "Capitão de Mar e Guerra (IM)", "Capitão de Fragata (IM)",
            "Capitão de Corveta (IM)", "Capitão Tenente (IM)", "Outro"
        ]
        postos_geral = [
            "Primeiro-Tenente", "Segundo-Tenente", "Suboficial",
            "Primeiro-Sargento", "Segundo-Sargento", "Terceiro-Sargento", "Cabo", "Outro"
        ]
        postos = postos_ord if self.categoria in ["ordenador_de_despesa", "agente_fiscal"] else postos_geral
        self.posto_input.clear()
        self.posto_input.addItems(postos)

    def atualizar_abreviacao(self, posto):
        abrev_ord = {
            "Capitão de Mar e Guerra (IM)": ["CMG (IM)", "Outro"],
            "Capitão de Fragata (IM)": ["CF (IM)", "Outro"],
            "Capitão de Corveta (IM)": ["CC (IM)", "Outro"],
            "Capitão Tenente (IM)": ["CT (IM)", "Outro"],
            "Outro": ["Outro"]
        }
        abrev_geral = {
            "Capitão de Mar e Guerra(IM)": ["CMG(IM)", "Outro"],
            "Capitão de Fragata(IM)": ["CF(IM)", "Outro"],
            "Capitão de Corveta(IM)": ["CC(IM)", "Outro"],
            "Capitão Tenente(IM)": ["CT(IM)", "Outro"],            
            "Primeiro-Tenente(IM)": ["1ºTEN(IM)", "Outro"],
            "Primeiro-Tenente(RM2-T)": ["1ºTEN(RM2-T)", "Outro"],
            "Segundo-Tenente(IM)": ["2ºTEN(IM)", "Outro"],
            "Segundo-Tenente(RM2-T)": ["2ºTEN(RM2-T)", "Outro"],
            "Suboficial": ["SO", "Outro"],
            "Primeiro-Sargento": ["1º SG", "Outro"],
            "Segundo-Sargento": ["2º SG", "Outro"],
            "Terceiro-Sargento": ["3º SG", "Outro"],
            "Cabo": ["CB", "Outro"],
            "Outro": ["Outro"]
        }
        abrev_map = abrev_ord if self.categoria in ["ordenador_de_despesa", "agente_fiscal"] else abrev_geral
        self.abrev_posto_input.clear()
        self.abrev_posto_input.addItems(abrev_map.get(posto, ["Outro"]))

    def inicializar_funcoes(self):
        funcoes = ["Função 1", "Função 2", "Função 3", "Outro"]
        self.funcao_input.clear()
        self.funcao_input.addItems(funcoes)

    def get_data(self):
        return {
            "Nome": self.nome_input.text(),
            "Nome de Guerra": self.nome_guerra_input.text(),
            "Posto": self.posto_input.currentText(),
            "Abreviação": self.abrev_posto_input.currentText(),
            "NIP": self.nip_input.text(),
            "Função": self.funcao_input.currentText()
        }
