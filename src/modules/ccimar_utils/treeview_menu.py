from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt, QSize


class TreeMenu(QTreeView):
    def __init__(self, icons, owner, parent=None):
        """
        :param owner: Objeto que contém os métodos de callback.
        """
        super().__init__(parent)
        self.icons = icons
        self.owner = owner
        self.setHeaderHidden(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Desativa a edição via duplo clique.
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setStyleSheet("""
            QTreeView { 
                color: #FFF; 
                font-size: 14px; 
            }
            QTreeView::item:hover {
                background-color: #2C2F3F;
                border: none;
            }
            QTreeView::item:selected {
                background-color: #44475A;
                border: 1px solid #6272A4;
                outline: none;
            }
            QTreeView::item:focus {
                outline: none;
            }
        """)
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.populate_tree()
        self.expandAll()
        # Conecta o clique único para tratar a abertura/fechamento dos itens pais.
        self.clicked.connect(self.handle_item_click)

    def populate_tree(self):
        def add_item(parent, text, callback):
            item = QStandardItem(text)
            item.setData(lambda: callback(self.owner), Qt.ItemDataRole.UserRole)
            parent.appendRow(item)

        # Define icon size
        icon_size = 24  # Adjust if needed

        # Parent items with icons
        item_relatorios   = QStandardItem(self.icons.get("statistics_azul", QIcon()), "Relatórios")
        item_oficios      = QStandardItem(self.icons.get("mensagem", QIcon()), "Ofícios")
        item_webscrapping = QStandardItem(self.icons.get("magnifying-glass", QIcon()), "Webscrapping")
        item_api          = QStandardItem(self.icons.get("api", QIcon()), "API")

        # Set icon size for parent items
        for item in [item_relatorios, item_oficios, item_webscrapping, item_api]:
            item.setSizeHint(QSize(icon_size + 10, icon_size + 10))

        # Itens filhos com callbacks
        add_item(item_oficios, "Ofício do CCIMAR-20", self.owner.show_oficio_ccimar20_widget)
        add_item(item_api, "Gerar Notas", self.owner.show_gerar_notas_widget)
        add_item(item_relatorios, "Consultas do Airflow", self.owner.show_relatorio_consultas_airflow_widget)
        add_item(item_relatorios, "Relatório SGM", self.owner.show_relatorio_sgm_widget)
        add_item(item_relatorios, "Relatório CCIMAR-11", self.owner.show_relatorio_ccimar11_widget)
        add_item(item_relatorios, "Relatório COFAMAR", self.owner.show_relatorio_cofamar_widget)
        add_item(item_relatorios, "Gerar Nota com Cálculo Total", self.owner.show_relatorio_calculo_total_widget)
        add_item(item_relatorios, "Notas Monitoradas", self.owner.show_relatorio_notas_monitoradas_widget)
        add_item(item_relatorios, "AUDCONT - Notas Vencidas", self.owner.show_relatorio_audcont_widget)
        add_item(item_webscrapping, "Teste", self.owner.show_teste_widget)

        # Adiciona os itens pais ao modelo
        self.model.appendRow(item_relatorios)
        self.model.appendRow(item_oficios)
        self.model.appendRow(item_webscrapping)
        self.model.appendRow(item_api)


    def handle_item_click(self, index):
        item = self.model.itemFromIndex(index)
        if item.hasChildren():
            if self.isExpanded(index):
                self.collapse(index)
            else:
                self.expand(index)
        else:
            callback = item.data(Qt.ItemDataRole.UserRole)
            if callable(callback):
                callback()
