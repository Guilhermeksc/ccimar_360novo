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
from .add_dialog import AddDialog
from .edit_dialog import EditDialog
from utils.styles.style_add_button import add_button_func
from pathlib import Path
from paths import (
    update_dir, save_config, get_config_value,
    DEFAULT_DATABASE_DIR, DEFAULT_JSON_DIR, DEFAULT_TEMPLATE_DIR, reload_paths,
    AGENTES_RESPONSAVEIS_FILE
)
def create_agentes_responsaveis(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Criando e adicionando o widget AgentesResponsaveisWidget
    agentes_widget = AgentesResponsaveisWidget(icons)
    main_layout.addWidget(agentes_widget)
    
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

                
class AgentesResponsaveisWidget(QWidget):
    def __init__(self, icons, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Criação da barra de título e botões
        title_widget, self.btn_export, self.btn_import, self.btn_add, self.btn_delete = self.create_title_bar()
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
        dialog = EditDialog(data, self.icons, parent=self)
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

        btn_export = add_button_func("Exportar", "export", self.export_table_data, layout, self.icons, tooltip="Exportar dados")
        btn_import = add_button_func("Importar", "import", self.import_table_data, layout, self.icons, tooltip="Importar dados")
        btn_add = add_button_func("Adicionar", "add", self.open_add_dialog, layout, self.icons, tooltip="Adicionar novo agente")
        btn_delete = add_button_func("Excluir", "delete", self.delete_selected_rows, layout, self.icons, tooltip="Excluir itens selecionados")
      
        return title_widget, btn_export, btn_import, btn_add, btn_delete

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

    def open_add_dialog(self):
        # Dados iniciais vazios para um novo agente
        data = {"Nome": "", "Nome de Guerra": "", "Posto": "", "Abreviação": "", "NIP": "", "Função": ""}
        dialog = AddDialog(data, self.icons, parent=self)
        dialog.setWindowTitle("Adicionar Responsáveis")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            model = self.table.model()
            row = model.rowCount()
            model.insertRow(row)
            # Cria o item checkbox
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            model.setItem(row, 0, check_item)
            # Insere os dados
            model.setItem(row, 1, QStandardItem(new_data["Nome"]))
            model.setItem(row, 2, QStandardItem(new_data["Nome de Guerra"]))
            model.setItem(row, 3, QStandardItem(new_data["Posto"]))
            model.setItem(row, 4, QStandardItem(new_data["Abreviação"]))
            model.setItem(row, 5, QStandardItem(new_data["NIP"]))
            model.setItem(row, 6, QStandardItem(new_data["Função"]))
            self.save_data_to_json()

    def save_data_to_json(self):
        model = self.table.model()
        new_data = []
        for row_idx in range(model.rowCount()):
            agent = {
                "Nome": model.item(row_idx, 1).text() if model.item(row_idx, 1) else "",
                "Nome de Guerra": model.item(row_idx, 2).text() if model.item(row_idx, 2) else "",
                "Posto": model.item(row_idx, 3).text() if model.item(row_idx, 3) else "",
                "Abreviação": model.item(row_idx, 4).text() if model.item(row_idx, 4) else "",
                "NIP": model.item(row_idx, 5).text() if model.item(row_idx, 5) else "",
                "Funcao": model.item(row_idx, 6).text() if model.item(row_idx, 6) else ""
            }
            new_data.append(agent)
        try:
            with open(AGENTES_RESPONSAVEIS_FILE, 'w', encoding='utf-8') as file:
                json.dump({"imported_data": new_data}, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao escrever no arquivo JSON: {e}")

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
