# src/modules/ccimar11_planejamento/menu/treeview_menu.py

from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from .menu_callbacks import (
    show_criterios_pesos, show_cadastro_objetivos_navais, show_objetivos_navais, 
    show_acoes_orcamentarias, show_objetos_auditaveis, show_om_representativas,  
    show_criterio1_execucao_licitacao, show_criterio2_pagamento,
    show_criterio3_munic, show_criteriox_omps, show_criterio4_patrimonio,
    show_oficio_ccimar20_widget, show_gerar_notas_widget, show_chat_bot
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
        item_criterios_pesos = add_parent("Planejamento", self.icons["prioridade"], show_criterios_pesos)
        add_item(item_criterios_pesos, "Cadastro - Obj.Auditáveis", self.icons, show_cadastro_objetivos_navais)
        add_item(item_criterios_pesos, "Objetivos Navais", self.icons, show_objetivos_navais)
        add_item(item_criterios_pesos, "Ações Orçamentárias", self.icons, show_acoes_orcamentarias)
        add_item(item_criterios_pesos, "Anexo A - Obj.Auditáveis", self.icons, show_objetos_auditaveis)
        add_item(item_criterios_pesos, "Anexo B - OM Represent.", self.icons, show_om_representativas)

        item_paint = add_parent("PAINT", self.icons["analytics"])
        item_raint = add_parent("RAINT", self.icons["report"])
        item_cronograma = add_parent("Cronograma", self.icons["timeline"])
        item_processo = add_parent("Processo de Auditoria", self.icons["process"])
        item_monitoramento = add_parent("Monitoramento", self.icons["statistics"], show_oficio_ccimar20_widget)
        item_chat = add_parent("Chat", self.icons["chat"], show_chat_bot)

        # Adding child items with their respective callbacks
        add_item(item_paint, "Execução/Licitação", self.icons, show_criterio1_execucao_licitacao)
        add_item(item_paint, "Pagamento", self.icons, show_criterio2_pagamento)
        add_item(item_paint, "Municiamento", self.icons, show_criterio3_munic)
        add_item(item_paint, "Patrimônio", self.icons, show_criterio4_patrimonio)
        add_item(item_paint, "Última Auditoria", self.icons, show_criterio3_munic)
        add_item(item_paint, "Notas de Auditoria", self.icons, show_criterio3_munic)
        add_item(item_paint, "Foco Externo", self.icons, show_criterio3_munic)
        add_item(item_paint, "OC", self.icons, show_criterio3_munic)
        add_item(item_paint, "OMPS", self.icons, show_criteriox_omps)
        add_item(item_processo, "Plano de Auditoria", self.icons, show_criteriox_omps)
        add_item(item_processo, "Mensagem", self.icons, show_criteriox_omps)
        add_item(item_processo, "OS de Designação", self.icons, show_criteriox_omps)
        add_item(item_processo, "Ofício de Apresentação", self.icons, show_criteriox_omps)
        add_item(item_processo, "Solicitação de Auditoria (SA)", self.icons, show_criteriox_omps)

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
