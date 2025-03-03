from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtSql import QSqlTableModel
from utils.search_bar import setup_search_bar, MultiColumnFilterProxyModel
from utils.add_button import add_button
from assets.styles.styles import table_view_stylesheet, title_view_stylesheet
import pandas as pd

class CartaoCorporativoView(QMainWindow):
    # Signals for communication with the controller
    refreshRequested = pyqtSignal()
    rowDoubleClicked = pyqtSignal(dict)
    linkDataCartaoPagamentoGov = pyqtSignal()
    open_dashboard = pyqtSignal() 

    def __init__(self, icons, model, database_path, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.database_path = database_path
        self.selected_row_data = None

        # 🔹 Agora model é um QSqlTableModel válido
        self.model = model  

        # 🔹 Inicializa proxy model corretamente
        self.proxy_model = MultiColumnFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)  # ✅ Agora recebe um QSqlTableModel corretamente
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.setup_ui()

    def setup_ui(self):
        # Set main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Title bar
        title_layout = QHBoxLayout()
        label_title = QLabel("Cartão Corporativo", self)
        label_title.setStyleSheet(title_view_stylesheet())
        title_layout.addWidget(label_title)
        title_layout.addStretch()
        self.main_layout.addLayout(title_layout)

        # Top layout for search and buttons
        top_layout = QHBoxLayout()
        self.search_bar = setup_search_bar(self.icons, top_layout, self.proxy_model)
        self.setup_buttons(top_layout)
        self.main_layout.addLayout(top_layout)

        # Table setup
        self.setup_table_view()
        self.configure_table_model()
        self.adjust_columns()

    def setup_buttons(self, layout):
        """Adiciona botões de ação."""
        add_button("URL", "link", self.linkDataCartaoPagamentoGov, layout, self.icons, tooltip="Abrir site de dados")
        add_button("Refresh", "excel", self.refreshRequested, layout, self.icons, tooltip="Atualizar dados")
        add_button("Export", "word", self.refreshRequested, layout, self.icons, tooltip="Exportar para Excel")
        add_button("Dashboard", "dashboard", self.open_dashboard, layout, self.icons, tooltip="Abrir dashboard")  # 🔹 Novo botão


    def setup_table_view(self):
        """Setup the table for displaying corporate card transactions."""
        self.table_view = QTableView(self)
        self.table_view.setModel(self.proxy_model)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.doubleClicked.connect(self.on_table_double_click)

        # Table behavior
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setStyleSheet(table_view_stylesheet())

        # Center align delegate for cells
        center_delegate = CenterAlignDelegate(self.table_view)
        for column in range(self.model.columnCount()):
            self.table_view.setItemDelegateForColumn(column, center_delegate)

        # Custom delegate for transaction type (icons)
        transaction_col = self.model.fieldIndex("transacao")
        self.table_view.setItemDelegateForColumn(transaction_col, CustomTransactionDelegate(self.icons, self.table_view, self.model))

        self.main_layout.addWidget(self.table_view)

    def configure_table_model(self):
        """Configure headers and filtering."""
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.update_column_headers()
        self.hide_unwanted_columns()

    def update_column_headers(self):
        """Set readable column names."""
        titles = {
            0: "ID", 1: "Órgão Superior", 3: "Órgão", 5: "Unidade Gestora",
            7: "Ano", 8: "Mês", 9: "CPF Portador", 10: "Nome Portador",
            11: "CNPJ/CPF Favorecido", 12: "Favorecido", 13: "Transação",
            14: "Data", 15: "Valor"
        }
        for column, title in titles.items():
            self.model.setHeaderData(column, Qt.Orientation.Horizontal, title)

    def hide_unwanted_columns(self):
        """Hide non-relevant columns."""
        visible_columns = {0, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15}
        for column in range(self.model.columnCount()):
            if column not in visible_columns:
                self.table_view.hideColumn(column)

    def adjust_columns(self):
        """Adjust column sizes for readability."""
        self.table_view.resizeColumnsToContents()
        QTimer.singleShot(1, self.apply_custom_column_sizes)

    def apply_custom_column_sizes(self):
        """Apply fixed and stretch column sizes."""
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(15, QHeaderView.ResizeMode.Fixed)

        header.resizeSection(0, 50)
        header.resizeSection(5, 100)
        header.resizeSection(7, 70)
        header.resizeSection(12, 200)
        header.resizeSection(15, 100)

    def on_table_double_click(self, index):
        """Handle double-click to open transaction details."""
        row = self.proxy_model.mapToSource(index).row()
        transaction_id = self.model.index(row, self.model.fieldIndex("id")).data()

        self.selected_row_data = self.load_data_by_id(transaction_id)
        if self.selected_row_data:
            self.rowDoubleClicked.emit(self.selected_row_data)
        else:
            QMessageBox.warning(self, "Erro", "Falha ao carregar dados da transação selecionada.")

    def load_data_by_id(self, transaction_id):
        """Fetch transaction details from database using its ID."""
        query = f"SELECT * FROM tabela_cartao_corporativo WHERE id = '{transaction_id}'"
        try:
            data = self.model.database_manager.fetch_all(query)
            if isinstance(data, list):
                data = pd.DataFrame(data, columns=self.model.column_names)
            return data.iloc[0].to_dict() if not data.empty else None
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return None

    def export_to_excel(self):
        """Export the current table data to an Excel file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save as Excel", "", "Excel Files (*.xlsx)")

        if file_path:
            data = self.model.database_manager.fetch_all("SELECT * FROM tabela_cartao_corporativo")
            df = pd.DataFrame(data, columns=self.model.column_names)
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Sucesso", f"Dados exportados para {file_path}")

class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        """Align text in cells to the center."""
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

class CustomTransactionDelegate(QStyledItemDelegate):
    def __init__(self, icons, parent=None, model=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model

    def paint(self, painter, option, index):
        """Display icons for transaction types."""
        if index.column() == self.model.fieldIndex("transacao"):
            transaction_type = index.data(Qt.ItemDataRole.DisplayRole)

            icon_map = {
                "COMPRA A/V - R$ - APRES": "shopping_cart",
                "TRANSFERÊNCIA A/V": "transfer",
                "SERVIÇO A/V": "service",
                "SAQUE": "withdrawal",
            }
            icon_key = icon_map.get(transaction_type, None)

            if icon_key and icon_key in self.icons:
                icon = self.icons[icon_key]
                icon_size = 24
                icon_rect = QRect(option.rect.left() + 5, option.rect.top() + (option.rect.height() - icon_size) // 2, icon_size, icon_size)
                painter.drawPixmap(icon_rect, icon.pixmap(icon_size, icon_size))
            else:
                super().paint(painter, option, index)
