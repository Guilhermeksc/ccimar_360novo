from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from utils.styles.style_add_button import add_button_func
from utils.linha_layout import linha_divisoria_sem_spacer_layout
from .config_Responsaveis.edit_responsaveis import EditPredefinicoesDialog
from paths import *
import os
import json
import pandas as pd
import subprocess
from .config_OM.edit_OM import show_organizacoes_widget
from .config_Setores.edit_Setores import show_setores_widget
from utils.styles.style_add_button import apply_button_style
from utils.styles.style_table import apply_table_style
from utils.styles.styles_edit_button import apply_edit_dialog_style

class ConfigManager(QWidget):
    def __init__(self, icons, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.setup_ui()
        self.current_content_layout = None
        # self.contratos_manager = ContratosManager(self.icons, dados={})

    def setup_ui(self):
        """Configura o layout de configuração com um menu lateral."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Menu lateral
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        # Botões do menu lateral
        button_style = """
            QPushButton {
                border: none;
                color: white;
                font-size: 16px; 
                text-align: center;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3A3B47; 
            }
            QPushButton:checked {
                background-color: #202124; 
                font-weight: bold;
            }
        """
        buttons = [
            ("Agentes Responsáveis", self.show_agentes_responsaveis_widget),
            ("Organizações Militares", self.show_organizacoes_widget),
        ]

        self.config_menu_buttons = []

        for text, callback in buttons:
            button = QPushButton(text)
            button.setCheckable(True)
            button.setStyleSheet(button_style)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(callback)
            button.clicked.connect(lambda _, b=button: self.set_selected_button(b))
            menu_layout.addWidget(button)
            self.config_menu_buttons.append(button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        menu_layout.addItem(spacer)

        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        menu_widget.setStyleSheet("background-color: #181928;")
        main_layout.addWidget(menu_widget, stretch=1)
        menu_widget.setFixedWidth(250)  # Largura fixa para o menu
        # Área de conteúdo
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        main_layout.addWidget(self.content_widget, stretch=4)

    def set_selected_button(self, selected_button):
        """Define o botão selecionado no menu lateral."""
        for button in self.config_menu_buttons:
            button.setChecked(False)
        selected_button.setChecked(True)

    def clear_content(self):
        """Limpa o layout atual do content_widget."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        """Recursivamente limpa um layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def show_agentes_responsaveis_widget(self):
        """Exibe o widget para Alteração dos Agentes Responsáveis."""
        self.clear_content()  # Limpa o conteúdo atual

        # Instancia o widget com a barra de título e a tabela
        agentes_widget = AgentesResponsaveisWidget(self)

        # Adiciona o widget à área de conteúdo (por exemplo, a um layout ou scroll area)
        self.content_layout.addWidget(agentes_widget)

    def show_organizacoes_widget(self):
        show_organizacoes_widget(self.content_layout, self.icons, self)

    def show_setores_requisitantes_widget(self):
        show_setores_widget(self.content_layout, self.icons, self)

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

                
class AgentesResponsaveisWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Criação da barra de título e botões
        title_widget, self.btn_export, self.btn_import, self.btn_delete = self.create_title_bar()
        main_layout.addWidget(title_widget)

        # Criação da tabela utilizando CustomTableView
        # Caso não tenha uma classe CustomTableView, use QTableView diretamente
        self.table = CustomTableView()
        self.table.setFont(QFont("Arial", 12))
        apply_table_style(self.table)

        # Criação do modelo e definição dos cabeçalhos
        # Agora temos 7 colunas: 1 de checkbox + 6 de dados
        model = QStandardItemModel(0, 7, self)
        model.setHorizontalHeaderLabels([
            "", "Nome", "Nome de Guerra", "Posto", "Abreviação", "NIP", "Função"
        ])
        self.table.setModel(model)

        # Ajuste das colunas (opcional; adapte se precisar ocultar colunas)
        self.adjust_columns()

        main_layout.addWidget(self.table)

        # Carregar dados do JSON
        self.load_data()

        # Conectar botões
        self.btn_export.clicked.connect(self.export_table_data)
        self.btn_import.clicked.connect(self.import_table_data)
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        self.table.doubleClicked.connect(self.open_edit_dialog)
        
        self.setLayout(main_layout)

    def open_edit_dialog(self, index):
        if not index.isValid():
            return
        row = index.row()
        model = self.table.model()
        data = {
            "Nome": model.item(row, 1).text() if model.item(row, 1) else "",
            "Nome de Guerra": model.item(row, 2).text() if model.item(row, 2) else "",
            "Posto": model.item(row, 3).text() if model.item(row, 3) else "",
            "Abreviação": model.item(row, 4).text() if model.item(row, 4) else "",
            "NIP": model.item(row, 5).text() if model.item(row, 5) else "",
            "Função": model.item(row, 6).text() if model.item(row, 6) else ""
        }
        dialog = EditDialog(data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            model.setItem(row, 1, QStandardItem(new_data["Nome"]))
            model.setItem(row, 2, QStandardItem(new_data["Nome de Guerra"]))
            model.setItem(row, 3, QStandardItem(new_data["Posto"]))
            model.setItem(row, 4, QStandardItem(new_data["Abreviação"]))
            model.setItem(row, 5, QStandardItem(new_data["NIP"]))
            model.setItem(row, 6, QStandardItem(new_data["Função"]))
            
    def create_title_bar(self):
        title_widget = QWidget()
        layout = QHBoxLayout(title_widget)

        title_label = QLabel("Inclusão / Exclusão de Agentes Responsáveis")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_label)
        layout.addStretch()

        btn_export = QPushButton("Exportar")
        apply_button_style(btn_export)
        layout.addWidget(btn_export)

        btn_import = QPushButton("Importar")
        apply_button_style(btn_import)
        layout.addWidget(btn_import)

        btn_delete = QPushButton("Excluir")
        apply_button_style(btn_delete)
        layout.addWidget(btn_delete)

        return title_widget, btn_export, btn_import, btn_delete

    def adjust_columns(self):
        # Define larguras fixas para algumas colunas
        self.table.setColumnWidth(0, 30)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(6, 400)

        header = self.table.horizontalHeader()
        model = self.table.model()
        for col in range(model.columnCount()):
            if col == 1:  # Coluna que deve ocupar o espaço restante
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
                    
        self.table.hideColumn(2)
        self.table.hideColumn(4)
        self.table.hideColumn(5)

    def load_data(self):
        """Carrega os dados do arquivo JSON e popula o modelo."""
        try:
            with open(AGENTES_RESPONSAVEIS_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        agentes_list = []
        for key, agents in data.items():
            for agent in agents:
                agent.setdefault("Nome de Guerra", "")
                agent.setdefault("NIP", "")
                agentes_list.append(agent)

        model = self.table.model()
        model.setRowCount(len(agentes_list))

        for row, agent in enumerate(agentes_list):
            # Cria item checkbox na primeira coluna
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            model.setItem(row, 0, check_item)

            # Demais colunas
            model.setItem(row, 1, QStandardItem(agent.get("Nome", "")))
            model.setItem(row, 2, QStandardItem(agent.get("Nome de Guerra", "")))
            model.setItem(row, 3, QStandardItem(agent.get("Posto", "")))
            model.setItem(row, 4, QStandardItem(agent.get("Abreviacao", "")))
            model.setItem(row, 5, QStandardItem(agent.get("NIP", "")))
            model.setItem(row, 6, QStandardItem(agent.get("Funcao", "")))

    def export_table_data(self):
        """Exporta os dados da tabela para um arquivo Excel (xlsx) e o abre."""
        model = self.table.model()
        rowCount = model.rowCount()
        colCount = model.columnCount()

        headers = [model.headerData(col, Qt.Orientation.Horizontal) for col in range(colCount)]
        data = []
        for row in range(rowCount):
            row_data = {}
            for col in range(colCount):
                if col == 0:  # Ignora a coluna de seleção
                    continue
                item = model.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            data.append(row_data)

        df = pd.DataFrame(data)
        filename = "exported_agentes.xlsx"

        try:
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                worksheet.set_column(0, 0, 30)  # Nome
                worksheet.set_column(1, 1, 20)  # Nome de Guerra
                worksheet.set_column(2, 2, 20)  # Posto
                worksheet.set_column(3, 3, 15)  # Abreviação
                worksheet.set_column(4, 4, 10)  # NIP
                worksheet.set_column(5, 5, 30)  # Função
        except PermissionError:
            print("Erro: O arquivo 'exported_agentes.xlsx' já está aberto. Feche-o e tente novamente.")
            QMessageBox.critical(self, "Erro", "O arquivo 'exported_agentes.xlsx' já está aberto. Feche-o e tente novamente.")
            return

        try:
            os.startfile(filename)
        except AttributeError:
            subprocess.call(["xdg-open", filename])

    def import_table_data(self):
        """
        Importa os dados de um arquivo XLSX ou CSV,
        atualiza a tabela e salva os dados no arquivo JSON.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Dados",
            "",
            "Planilhas (*.xlsx *.xls *.csv);;Todos os Arquivos (*)"
        )
        if not file_path:
            return  # Usuário cancelou

        try:
            if file_path.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

        required_columns = ["Nome", "Nome de Guerra", "Posto", "Abreviação", "NIP", "Função"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"Colunas ausentes no arquivo: {missing_cols}")
            return

        def to_str(value):
            if pd.isna(value):
                return ""
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)

        imported_data = []
        for _, row in df.iterrows():
            agent = {
                "Nome": to_str(row.get("Nome", "")),
                "Nome de Guerra": to_str(row.get("Nome de Guerra", "")),
                "Posto": to_str(row.get("Posto", "")),
                "Abreviacao": to_str(row.get("Abreviação", "")),
                "NIP": to_str(row.get("NIP", "")),
                "Funcao": to_str(row.get("Função", ""))
            }
            imported_data.append(agent)

        # Atualiza o modelo da tabela
        model = self.table.model()
        model.setRowCount(len(imported_data))
        for row_idx, agent in enumerate(imported_data):
            # Checkbox na coluna 0
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            model.setItem(row_idx, 0, check_item)

            model.setItem(row_idx, 1, QStandardItem(agent["Nome"]))
            model.setItem(row_idx, 2, QStandardItem(agent["Nome de Guerra"]))
            model.setItem(row_idx, 3, QStandardItem(agent["Posto"]))
            model.setItem(row_idx, 4, QStandardItem(agent["Abreviacao"]))
            model.setItem(row_idx, 5, QStandardItem(agent["NIP"]))
            model.setItem(row_idx, 6, QStandardItem(agent["Funcao"]))

        # Sobrescreve o arquivo JSON com os dados importados
        try:
            with open(AGENTES_RESPONSAVEIS_FILE, 'w', encoding='utf-8') as file:
                json.dump({"imported_data": imported_data}, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao escrever no arquivo JSON: {e}")

    def delete_selected_rows(self):
        """
        Exclui do modelo (e do arquivo JSON) as linhas cujo checkbox estiver marcado.
        """
        model = self.table.model()
        rows_to_remove = []

        # Verifica todas as linhas para saber quais estão marcadas
        for row in range(model.rowCount()):
            item = model.item(row, 0)  # Coluna do checkbox
            if item and item.checkState() == Qt.CheckState.Checked:
                rows_to_remove.append(row)

        # Remove primeiro as linhas de baixo para cima, evitando reindexação
        for row in reversed(rows_to_remove):
            model.removeRow(row)

        # Reconstrói a lista de agentes a partir do modelo
        new_data = []
        for row_idx in range(model.rowCount()):
            # Ignoramos a coluna 0 (checkbox)
            agent = {
                "Nome": model.item(row_idx, 1).text() if model.item(row_idx, 1) else "",
                "Nome de Guerra": model.item(row_idx, 2).text() if model.item(row_idx, 2) else "",
                "Posto": model.item(row_idx, 3).text() if model.item(row_idx, 3) else "",
                "Abreviacao": model.item(row_idx, 4).text() if model.item(row_idx, 4) else "",
                "NIP": model.item(row_idx, 5).text() if model.item(row_idx, 5) else "",
                "Funcao": model.item(row_idx, 6).text() if model.item(row_idx, 6) else ""
            }
            new_data.append(agent)

        # Sobrescreve o arquivo JSON com a lista atualizada
        try:
            with open(AGENTES_RESPONSAVEIS_FILE, 'w', encoding='utf-8') as file:
                json.dump({"imported_data": new_data}, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao escrever no arquivo JSON: {e}")

class EditDialog(QDialog):
    def __init__(self, data, categoria="geral", parent=None):
        super().__init__(parent)
        self.categoria = categoria
        apply_edit_dialog_style(self)
        self.setWindowTitle("Editar Agente")
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
