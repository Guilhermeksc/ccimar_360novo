# src/modules/ccimar11_planejamento/menu/treeview_menu.py

from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from .menu_callbacks import (  
    show_criterio1_execucao_licitacao, show_criterio2_pagamento, show_chat_bot_local,
    show_criterio3_munic, show_criteriox_omps, show_criterio4_patrimonio,
    show_conselho_de_gestao, show_gerar_notas_widget, show_chat_bot
)

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
        def add_item(parent, text, callback):
            """Adds a child item with a callback."""
            item = QStandardItem(text)
            item.setData(lambda: callback(self.owner), Qt.ItemDataRole.UserRole)
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
        item_paint = add_parent("Auditores", self.icons["auditor"])
        item_relatorio = add_parent("Ordem de Serviço", self.icons["report"])
        item_monitoramento = add_parent("Conselho de Gestão", self.icons["meeting"], show_conselho_de_gestao)

        # Adding child items with their respective callbacks
        add_item(item_paint, "Escalação", show_criterio1_execucao_licitacao)
        add_item(item_relatorio, "Modelo 1", show_criteriox_omps)
        add_item(item_relatorio, "Modelo 2", show_criteriox_omps)
        add_item(item_monitoramento, "Slide", show_conselho_de_gestao)
        add_item(item_monitoramento, "Monitoramento 2", show_gerar_notas_widget)


    def handle_item_click(self, index):
        """Handles item click events and executes the associated callback."""
        item = self.model.itemFromIndex(index)
        callback = item.data(Qt.ItemDataRole.UserRole)

        if item.hasChildren():
            if self.isExpanded(index):
                self.collapse(index)
            else:
                self.expand(index)
        
        # Execute the callback if the item has one
        if callable(callback):
            callback()
