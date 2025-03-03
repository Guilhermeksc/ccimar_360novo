# src/modules/ccimar11_planejamento/menu/treeview_menu.py

from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from .menu_callbacks import (
    show_criterios_pesos, show_objetivos_navais, show_objetos_auditaveis, show_om_representativas,  
    show_criterio1_execucao_licitacao, show_criterio2_pagamento,
    show_criterio3_munic, show_criteriox_omps, show_criterio4_patrimonio,
    show_oficio_ccimar20_widget, show_gerar_notas_widget, show_chat_bot
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
        item_criterios_pesos = add_parent("Critérios e Pesos", self.icons["criteria"], show_criterios_pesos)
        add_item(item_criterios_pesos, "Objetivos Navais", show_objetivos_navais)
        add_item(item_criterios_pesos, "Objetos Auditáveis", show_objetos_auditaveis)
        add_item(item_criterios_pesos, "OM Representativas", show_om_representativas)

        item_paint = add_parent("PAINT", self.icons["analytics"])
        item_raint = add_parent("RAINT", self.icons["report"])
        item_cronograma = add_parent("Cronograma", self.icons["timeline"])
        item_processo = add_parent("Processo de Auditoria", self.icons["process"])
        item_monitoramento = add_parent("Monitoramento", self.icons["statistics"], show_oficio_ccimar20_widget)
        item_chat = add_parent("Chat", self.icons["chat"], show_chat_bot)

        # Adding child items with their respective callbacks
        add_item(item_paint, "Execução/Licitação", show_criterio1_execucao_licitacao)
        add_item(item_paint, "Pagamento", show_criterio2_pagamento)
        add_item(item_paint, "Municiamento", show_criterio3_munic)
        add_item(item_paint, "Patrimônio", show_criterio4_patrimonio)
        add_item(item_paint, "Última Auditoria", show_criterio3_munic)
        add_item(item_paint, "Notas de Auditoria", show_criterio3_munic)
        add_item(item_paint, "Foco Externo", show_criterio3_munic)
        add_item(item_paint, "OC", show_criterio3_munic)
        add_item(item_paint, "OMPS", show_criteriox_omps)
        add_item(item_processo, "Plano de Auditoria", show_criteriox_omps)
        add_item(item_processo, "Mensagem", show_criteriox_omps)
        add_item(item_processo, "OS de Designação", show_criteriox_omps)
        add_item(item_processo, "Ofício de Apresentação", show_criteriox_omps)
        add_item(item_processo, "Solicitação de Auditoria (SA)", show_criteriox_omps)

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
