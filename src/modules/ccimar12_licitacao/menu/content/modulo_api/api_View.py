from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtSql import QSqlTableModel
from utils.search_bar import setup_search_bar, MultiColumnFilterProxyModel
from utils.styles.style_add_button import add_button
from utils.styles import table_view_stylesheet, title_view_stylesheet
import pandas as pd
from utils.styles.style_table import apply_table_style
from utils.styles.styles_edit_button import apply_edit_dialog_style
import sys
import requests
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class APIView(QMainWindow):
    linkDataCartaoPagamentoGov = pyqtSignal(dict)
    refreshRequested = pyqtSignal()
    rowDoubleClicked = pyqtSignal(dict)
    exportTable = pyqtSignal()
    open_dashboard = pyqtSignal()

    def __init__(self, icons, model, title_text, database_path, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.database_path = database_path
        self.selected_row_data = None
        self.model = model  
        self.title_text = title_text
        self.setup_ui()

    def setup_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        apply_edit_dialog_style(self.main_widget)

        # Barra de título
        title_layout = QHBoxLayout()
        self.title_label = QLabel("")  # Será atualizado conforme a aba selecionada
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        self.main_layout.addLayout(title_layout)

        # Frame com o QTabWidget
        tab_frame = QFrame()
        tab_layout = QVBoxLayout(tab_frame)
        self.tab_widget = QTabWidget()
        tab_layout.addWidget(self.tab_widget)
        self.tab_widget.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

        self.main_layout.addWidget(tab_frame)
        self.setup_tabs()

    def setup_tabs(self):
        tab_functions = {
            "PCA": lambda: create_tab_pca(self.icons),
            "Publicação": lambda: create_publicacao(self.icons),
            "2.13": lambda: create_tab_2_13(self.icons),
            "2.20": lambda: create_tab_2_20(self.icons),
            "2.21": lambda: create_tab_2_21(self.icons),
            "2.22": lambda: create_tab_2_22(self.icons),
            "2.22.1": lambda: create_tab_2_22_1(self.icons),
            "2.22.2": lambda: create_tab_2_22_2(self.icons),
            "2.22.3": lambda: create_tab_2_22_3(self.icons),
            "2.22.4": lambda: create_tab_2_22_4(self.icons),
            "2.28": lambda: create_tab_2_28(self.icons),
            "2.29": lambda: create_tab_2_29(self.icons),
            "2.3": lambda: create_tab_2_3(self.icons),
            "2.30": lambda: create_tab_2_30(self.icons),
            "2.31": lambda: create_tab_2_31(self.icons),
            "2.32": lambda: create_tab_2_32(self.icons),
            "2.33": lambda: create_tab_2_33(self.icons),
            "2.5": lambda: create_tab_2_5(self.icons),
        }

        full_titles = {
            "PCA": "Plano de Contratações Anual (PCA)",	
            "Publicação": "Consultar Contratações por Data de Publicação",
            "2.13": "2.13 Limite de Dispensa de Licitação (PDM)",
            "2.20": "2.20 Registro de Penalidade no SICAF",
            "2.21": "2.21 Ausência de negociação do valor da proposta.",
            "2.22": "2.22 Ausência de publicação do aviso do edital no Portal de Licitações",
            "2.22.1": "2.22.1 Ausência de divulgação no Portal de Licitações (Publicação de Inexigibilidade/Dispensa)",
            "2.22.2": "2.22.2 Ausência de divulgação no Portal de Licitações (Publicação de extrato do contrato)",
            "2.22.3": "2.22.3 Ausência de divulgação no Portal de Licitações (Publicação de extrato de ata de registro de preços)",
            "2.22.4": "2.22.4 Divulgação, no Portal de Licitações de documentos que não permite a pesquisa de conteúdos",
            "2.28": "2.28 Fragilidade na Estimativa da Demanda",
            "2.29": "2.29 Assinatura de documento nato-digital",
            "2.3": "2.3 Análise de Publicação de Matérias da Seção 3 do DOU",
            "2.30": "2.30 Aplicação de Sanções Administrativas",
            "2.31": "2.31 Fornecedor com restrição para contratação",
            "2.32": "2.32 Aplicabilidade da Lei Geral de Proteção de Dados (LGPD) aos Contratos",
            "2.33": "2.33 Dispensa Eletrônica",
            "2.5": "2.5 Análise Processual de Alta Materialidade",
        }

        for key, func in tab_functions.items():
            self.tab_widget.addTab(func(), key)

        def update_title(index):
            tab_key = self.tab_widget.tabText(index)
            full_title = full_titles.get(tab_key, "")
            self.title_label.setText(f"{self.title_text} - {full_title}")

        self.tab_widget.currentChanged.connect(update_title)
        if self.tab_widget.count() > 0:
            update_title(0)

class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        """Align text in cells to the center."""
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

def create_publicacao(icons):
    return PublicacaoWidget(icons)


def create_tab_2_13(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.13"))
    return widget

def create_tab_2_20(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.20"))
    return widget

def create_tab_2_21(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.21"))
    return widget

def create_tab_2_22(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22"))
    return widget

def create_tab_2_22_1(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.1"))
    return widget

def create_tab_2_22_2(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.2"))
    return widget

def create_tab_2_22_3(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.3"))
    return widget

def create_tab_2_22_4(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.4"))
    return widget

def create_tab_2_28(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.28"))
    return widget

def create_tab_2_29(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.29"))
    return widget

def create_tab_2_3(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.3"))
    return widget

def create_tab_2_30(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.30"))
    return widget

def create_tab_2_31(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.31"))
    return widget

def create_tab_2_32(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.32"))
    return widget

def create_tab_2_33(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.33"))
    return widget

def create_tab_2_5(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.5"))
    return widget

def get_available_years():
    current_year = QDate.currentDate().year()
    return [str(year) for year in range(2025, current_year + 2)]


def download_and_read_csv(year):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/00394502000144/pca/{year}/csv"
    response = requests.get(url)
    if response.status_code == 200:
        file_path = f"pca_{year}.csv"
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"CSV file for {year} downloaded successfully.")
        df = pd.read_csv(file_path, sep=";")  # Ajuste o separador conforme necessário
        print(df.head())  # Exibe o cabeçalho do arquivo

        # Convertendo a coluna 'Valor Total Estimado (R$)' para float
        df['Valor Total Estimado (R$)'] = (
            df['Valor Total Estimado (R$)']
            .astype(str)
            .str.replace(',', '.', regex=True)  # Substitui vírgulas por pontos
            .astype(float)  # Converte para float
        )
        
        # Garantindo que a coluna UASG seja string para filtragem correta
        df['UASG'] = df['UASG'].astype(str)
        
        return df
    else:
        print(f"Failed to download CSV for {year}: {response.status_code}")
        return None

def create_table_view(dataframe):
    table_view = QTableView()
    model = QStandardItemModel()
    
    grouped_df = dataframe.groupby(['Unidade Responsável', 'UASG'])[['Valor Total Estimado (R$)']].sum().reset_index()
    model.setHorizontalHeaderLabels(["Unidade Responsável", "UASG", "Valor Total Estimado (R$)"])
    
    for row in grouped_df.itertuples():
        # Formata o valor para o padrão brasileiro (R$ 00.000,00)
        valor = row[3]
        valor_str = f"R$ {valor:_.2f}".replace(".", ",").replace("_", ".")
        
        valor_item = QStandardItem(valor_str)
        if valor > 5000000:  # Se valor maior que 5 milhões
            valor_item.setForeground(QColor("red"))
            
        model.appendRow([
            QStandardItem(str(row[1])),
            QStandardItem(str(row[2])),
            valor_item
        ])
    
    table_view.setModel(model)
    table_view.setSortingEnabled(True)
    table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)  # Seleciona a linha inteira
    table_view.verticalHeader().setVisible(False)  # Oculta a coluna do índice
    table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)  # Impede edição
    apply_table_style(table_view)
    
    # Ajustando tamanho das colunas
    table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
    table_view.setColumnWidth(1, 100)
    table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
    table_view.setColumnWidth(2, 200)
    
    return table_view

def show_full_data_dialog(dataframe, selected_uasg):
    # Filtrar os dados correspondentes à UASG selecionada
    filtered_df = dataframe[dataframe['UASG'].astype(str) == selected_uasg]
    
    dialog = QDialog()
    dialog.setWindowTitle(f"Detalhes da UASG {selected_uasg}")
    layout = QVBoxLayout(dialog)
    
    table_view = QTableView()
    model = QStandardItemModel()
    
    model.setHorizontalHeaderLabels(filtered_df.columns.tolist())
    
    for row in filtered_df.itertuples(index=False):
        items = [QStandardItem(str(value)) for value in row]
        model.appendRow(items)
    
    table_view.setModel(model)
    table_view.setSortingEnabled(True)
    table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    table_view.verticalHeader().setVisible(False)
    table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
    apply_table_style(table_view)
    
    layout.addWidget(table_view)
    dialog.setLayout(layout)
    dialog.resize(800, 400)
    dialog.exec()


def create_tab_pca(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)

    top_layout = QHBoxLayout()
    
    label = QLabel("Plano de Contratações Anual (PCA)")
    top_layout.addWidget(label)
    
    combo_box = QComboBox()
    combo_box.addItems(get_available_years())
    top_layout.addWidget(combo_box)

    download_button = QPushButton("Download CSV")
    top_layout.addWidget(download_button)
    
    layout.addLayout(top_layout)
    
    table_view = QTableView()
    apply_table_style(table_view)
    layout.addWidget(table_view)
    
    def on_download_clicked():
        nonlocal table_view  # Corrigindo o erro ao definir 'nonlocal' antes da referência a 'table_view'
        selected_year = combo_box.currentText()
        df = download_and_read_csv(selected_year)
        if df is not None:
            new_table = create_table_view(df)
            new_table.doubleClicked.connect(lambda index: show_full_data_dialog(df, new_table.model().item(index.row(), 1).text()))
            layout.replaceWidget(table_view, new_table)
            table_view.deleteLater()
            table_view = new_table
    
    download_button.clicked.connect(on_download_clicked)
    
    return widget


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTableView, QMessageBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel
import requests
import pandas as pd
from datetime import datetime, timedelta


class PublicacaoTableModel(QAbstractTableModel):
    """ Model for displaying API data in QTableView. """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.headers = [
            "Número Compra", "Data Abertura", "Data Encerramento",
            "Processo", "Valor Estimado", "Valor Homologado",
            "Código Unidade", "Nome Unidade"
        ]

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
        return None

def format_brl(value):
    """ Format a number as BRL currency. """
    try:
        return locale.currency(float(value), grouping=True, symbol=True)
    except (ValueError, TypeError):
        return "R$ 0,00"
        
class PublicacaoWidget(QWidget):
    def __init__(self, icons):
        super().__init__()
        self.icons = icons
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Consultar Contratações por Data de Publicação"))

        # Dropdown for Modalidade
        self.modalidade_combobox = QComboBox()
        modalidades = [
            "1 - Leilão - Eletrônico", "2 - Diálogo Competitivo", "3 - Concurso",
            "4 - Concorrência - Eletrônica", "5 - Concorrência - Presencial",
            "6 - Pregão - Eletrônico", "7 - Pregão - Presencial", "8 - Dispensa",
            "9 - Inexigibilidade", "10 - Manifestação de Interesse",
            "11 - Pré-qualificação", "12 - Credenciamento", "13 - Leilão - Presencial",
            "14 - Inaplicabilidade da Licitação"
        ]
        self.modalidade_combobox.addItems(modalidades)
        layout.addWidget(QLabel("Modalidade de Contratação:"))
        layout.addWidget(self.modalidade_combobox)

        # Search Button
        self.search_button = QPushButton("Consultar")
        self.search_button.clicked.connect(self.fetch_data)
        layout.addWidget(self.search_button)

        # Table View
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

    def fetch_data(self):
        """ Fetch all pages of API data and display in QTableView with BRL formatting. """
        selected_modalidade = self.modalidade_combobox.currentText().split(" - ")[0]
        base_url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
        
        today = datetime.today()
        start_date = today - timedelta(days=365)
        
        # Ensure dates are formatted as YYYYMMDD
        params = {
            "dataInicial": start_date.strftime("%Y%m%d"),
            "dataFinal": today.strftime("%Y%m%d"),
            "codigoModalidadeContratacao": selected_modalidade,
            "cnpj": "00394502000144",
            "pagina": 1,
            "tamanhoPagina": 50
        }

        all_data = []
        try:
            while True:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if "data" not in data:
                    QMessageBox.warning(self, "Erro", "Nenhum dado encontrado.")
                    return

                # Process data
                for item in data["data"]:
                    row = [
                        item.get("numeroCompra", ""),
                        item.get("dataAberturaProposta", ""),
                        item.get("dataEncerramentoProposta", ""),
                        item.get("processo", ""),
                        format_brl(item.get("valorTotalEstimado", 0)),  # Format as BRL
                        format_brl(item.get("valorTotalHomologado", 0)),  # Format as BRL
                        item["unidadeOrgao"].get("codigoUnidade", ""),
                        item["unidadeOrgao"].get("nomeUnidade", ""),
                    ]
                    all_data.append(row)

                # Check if there are more pages
                if data.get("empty", True) or params["pagina"] >= data.get("totalPaginas", 0):
                    break
                params["pagina"] += 1

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Erro ao acessar a API:\n{e}")
            return

        # Display data in TableView
        self.table_view.setModel(PublicacaoTableModel(all_data))
