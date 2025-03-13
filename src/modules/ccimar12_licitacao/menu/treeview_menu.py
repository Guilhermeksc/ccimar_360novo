# src/modules/ccimar11_planejamento/menu/treeview_menu.py

from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from .menu_callbacks import (  
    show_nota_auditoria_teste1, show_nota_auditoria_teste2,
    show_nota_auditoria_teste3,
    show_oficio_ccimar20_widget, show_gerar_notas_widget,
    show_relatorio_consultas_airflow_widget, show_relatorio_sgm_widget,
    show_relatorio_ccimar11_widget, show_relatorio_cofamar_widget,
    show_relatorio_calculo_total_widget, show_relatorio_notas_monitoradas_widget,
    show_cartao_corporativo, show_teste_widget, show_vigencia_contratos,
    show_atas, show_limites_governanca
)

class CustomStandardItem(QStandardItem):
    def __init__(self, icons, text, icon_key=None):
        """
        :param icons: Dicionário completo de ícones.
        :param text: Texto do item.
        :param icon_key: (Opcional) Chave para definir um ícone específico.
        """
        super().__init__(text)
        self.icons = icons  # Armazena o dicionário completo
        if icon_key is not None and icon_key in icons:
            self.setIcon(icons[icon_key])
            
class TreeMenu(QTreeView):
    def __init__(self, icons, owner, parent=None):
        """
        :param owner: Object that contains the callback methods.
        :param icons: Dictionary containing icons.
        """
        super().__init__(parent)
        self.owner = owner
        self.icons = icons
        self.setHeaderHidden(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.populate_tree()
        self.expandAll()
        self.clicked.connect(self.handle_item_click)

        self.setStyleSheet("""
            QTreeView { 
                color: #FFF; 
                font-size: 16px; 
            }
            QTreeView::item:hover {
                background-color: #2C2F3F;
                border: #2C2F3F;
            }
            QTreeView::item:selected {
                background-color: #44475A;
                border: 1px solid #44475A;
            }
        """)

    def populate_tree(self):
        def add_item(parent, text, icons, callback, icon_key=None):
            item = CustomStandardItem(icons, text, icon_key)
            item.setData(lambda: callback(self.owner, icons), Qt.ItemDataRole.UserRole)
            parent.appendRow(item)

        def add_parent(text, icon, callback=None):
            """Adds a parent item with an optional callback."""
            item = QStandardItem(icon, text)
            if callback:
                # Passa tanto o owner quanto os icons para o callback
                item.setData(lambda: callback(self.owner, self.icons), Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)
            return item

        # Parent items with icons
        item_nota   = QStandardItem(self.icons["prioridade"], "Nota de Auditoria")
        item_evidencias   = QStandardItem(self.icons["statistics"], "Evidências")
        item_mensagem      = QStandardItem(self.icons["mensagem"], "Mensagens")
        item_email      = QStandardItem(self.icons["mail"], "E-mail")
        item_oficio      = QStandardItem(self.icons["doc"], "Ofícios")
        item_webscrapping = QStandardItem(self.icons["magnifying-glass"], "Webscrapping")
        item_api          = QStandardItem(self.icons["api"], "API")

        # Adding child items with their respective callbacks
        add_item(item_nota, "NA - Teste1", self.icons, show_nota_auditoria_teste1)
        add_item(item_nota, "NA - Teste2", self.icons, show_nota_auditoria_teste2)
        add_item(item_nota, "NA - Teste3", self.icons, show_nota_auditoria_teste3)
        add_item(item_oficio, "Ofício 1", self.icons, show_oficio_ccimar20_widget)
        add_item(item_evidencias, "Empresas inidôneas", self.icons, show_relatorio_sgm_widget)
        add_item(item_evidencias, "Controle PDM", self.icons, show_relatorio_ccimar11_widget)
        add_item(item_evidencias, "Valores Homologados", self.icons, show_cartao_corporativo)
        add_item(item_evidencias, "Dados Pessoais", self.icons, show_cartao_corporativo)
        add_item(item_evidencias, "Limites de Governança", self.icons, show_limites_governanca)
        add_item(item_evidencias, "Contratos", self.icons, show_vigencia_contratos)
        add_item(item_evidencias, "Atas", self.icons, show_atas)

        # Add parent items to the model
        self.model.appendRow(item_nota)
        self.model.appendRow(item_evidencias)
        self.model.appendRow(item_mensagem)
        self.model.appendRow(item_email)
        self.model.appendRow(item_oficio)
        self.model.appendRow(item_webscrapping)
        self.model.appendRow(item_api)

    def handle_item_click(self, index):
        """Handles item click events and executes the associated callback."""
        item = self.model.itemFromIndex(index)
        if item.hasChildren():
            if self.isExpanded(index):
                self.collapse(index)
            else:
                self.expand(index)
        else:
            callback = item.data(Qt.ItemDataRole.UserRole)
            if callable(callback):
                callback()  # Executes the function, now passing the view instance
