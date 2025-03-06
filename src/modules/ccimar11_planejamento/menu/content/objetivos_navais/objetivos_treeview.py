from PyQt6.QtWidgets import (QTreeView, QListWidget)
from PyQt6.QtGui import  QStandardItem, QDrag
from PyQt6.QtCore import Qt, QMimeData
import json
from .criterio_widget import CriterioWidget
from .json_utils import load_objetivos_navais_data, save_objetivos_navais_data
        
class CustomTreeView(QTreeView):
    def __init__(self, icons=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Habilita drops
        self.json_file_path = None
        self.update_callback = None
        
        # Configuração do estilo para os critérios
        self.setStyleSheet("""
            QTreeView {
                           background-color: transparent;
                color: #FFF;
                font-size: 14px;
            }
            /* Estilo base para todos os itens */
            QTreeView::item {
                color: #FFFFFF;
                height: 20px;
            }
            /* Perspectivas */
            QTreeView::item:!has-siblings:!has-children,
            QTreeView::branch:!has-siblings:!has-children {
                font-size: 16px;
                font-weight: bold;
                color: #8AB4F7;  /* Azul principal */
            }
            /* OBNAV */
            QTreeView::item:has-siblings:!has-children,
            QTreeView::branch:has-siblings:!has-children {
                font-size: 15px;
                font-weight: 700;
                color: #4C8BF5;  /* Azul mais escuro */
            }
            /* EN */
            QTreeView::item:has-siblings:has-children,
            QTreeView::branch:has-siblings:has-children {
                font-size: 14px;
                font-weight: 600;
                font-style: italic;
                color: #B6D4FF;  /* Azul mais claro */
            }
            /* AEN */
            QTreeView::item:has-children,
            QTreeView::branch:has-children {
                font-size: 13px;
                font-weight: 500;
                color: #63A1FF;  /* Azul médio */
            }
            /* Critérios */
            QTreeView::item,
            QTreeView::branch {
                font-size: 12px;
                font-weight: normal;
                color: #E8F1FF;  /* Azul muito claro */
            }
            QTreeView::item:selected {
                background-color: #3B71CA;  /* Azul escuro para seleção */
            }
            QTreeView::item:hover {
                background-color: #1E3A8A;  /* Azul muito escuro para hover */
            }
        """)

    def remove_criterio(self, criterio_item):
        """Remove um critério do TreeView e do arquivo JSON"""
        print("[DEBUG] Tentando remover critério")
        if not criterio_item:
            print("[DEBUG] Critério item é None")
            return
            
        # Obtém o item AEN pai
        aen_item = criterio_item.parent()
        if not aen_item:
            print("[DEBUG] AEN pai não encontrado")
            return
            
        # Obtém os dados da AEN
        aen_data = aen_item.data(Qt.ItemDataRole.UserRole)
        if not aen_data:
            print("[DEBUG] Dados da AEN não encontrados")
            return
            
        # Remove o critério do modelo visual
        criterio_text = criterio_item.data(Qt.ItemDataRole.UserRole)
        if criterio_text and criterio_text.startswith('criterio: '):
            criterio_text = criterio_text[len('criterio: '):]
        else:
            print("[DEBUG] Texto do critério não encontrado")
            return
            
        print(f"[DEBUG] Removendo critério: {criterio_text}")
        aen_item.removeRow(criterio_item.row())
        
        # Atualiza o arquivo JSON
        if self.json_file_path:
            data = load_objetivos_navais_data(self.json_file_path)
            if data:
                print("[DEBUG] Atualizando arquivo JSON")
                # Encontra e atualiza a AEN correta no JSON
                for perspectiva in data.get('perspectivas', []):
                    for obnav in perspectiva.get('obnavs', []):
                        for en in obnav.get('estrategias_navais', []):
                            for aen in en.get('acoes_estrategicas', []):
                                if (str(aen.get('numero')) == str(aen_data.get('numero')) and 
                                    aen.get('descricao') == aen_data.get('descricao')):
                                    if 'criterios_auditoria' in aen:
                                        if criterio_text in aen['criterios_auditoria']:
                                            aen['criterios_auditoria'].remove(criterio_text)
                                            print(f"[DEBUG] Critério removido do JSON: {criterio_text}")
                                            save_objetivos_navais_data(data, self.json_file_path)
                                            return
                                    break
                print("[DEBUG] Critério não encontrado no JSON para remoção")

    def add_criterio_to_tree(self, criterio, parent_item, data=None, is_initial_load=False):
        """Adiciona um critério ao TreeView"""
        print(f"[DEBUG] Adicionando critério ao TreeView: {criterio}")
        # Cria o item do critério
        criterio_item = QStandardItem()
        criterio_item.setEditable(False)
        criterio_item.setData(f"criterio: {criterio}", Qt.ItemDataRole.UserRole)
        criterio_item.setText("")  # Define texto vazio para evitar sobreposição
        
        # Cria o widget personalizado com o botão de exclusão
        widget = CriterioWidget(
            criterio,
            lambda item=criterio_item: self.remove_criterio(item)
        )
        
        # Insere o item na árvore como primeiro filho
        parent_item.insertRow(0, criterio_item)
        
        # Define o widget personalizado para o item
        self.setIndexWidget(criterio_item.index(), widget)
        print(f"[DEBUG] Widget personalizado definido para critério: {criterio}")
        
        return criterio_item

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            criterio = event.mimeData().text()
            drop_index = self.indexAt(event.position().toPoint())
            
            if drop_index.isValid():
                item = self.model().itemFromIndex(drop_index)
                
                # Se o drop foi em um critério, usa o pai dele como destino
                if item.data(Qt.ItemDataRole.UserRole) and str(item.data(Qt.ItemDataRole.UserRole)).startswith('criterio:'):
                    item = item.parent()
                    if not item:
                        event.ignore()
                        return
                
                # Verifica se é uma AEN
                parent = item.parent()
                if parent and parent.parent() and parent.parent().parent():  # É uma AEN
                    aen_data = item.data(Qt.ItemDataRole.UserRole)
                    
                    # Adiciona o critério à AEN
                    if 'criterios_auditoria' not in aen_data:
                        aen_data['criterios_auditoria'] = []
                    
                    if criterio not in aen_data['criterios_auditoria']:
                        # Adiciona ao modelo de dados
                        aen_data['criterios_auditoria'].append(criterio)
                        
                        # Adiciona visualmente ao TreeView usando o método add_criterio_to_tree
                        self.add_criterio_to_tree(criterio, item, aen_data)
                        
                        # Atualiza o arquivo JSON
                        if self.json_file_path:
                            data = load_objetivos_navais_data(self.json_file_path)
                            if data:
                                # Encontra e atualiza a AEN correta no JSON
                                for perspectiva in data.get('perspectivas', []):
                                    for obnav in perspectiva.get('obnavs', []):
                                        for en in obnav.get('estrategias_navais', []):
                                            for aen in en.get('acoes_estrategicas', []):
                                                if (str(aen.get('numero')) == str(aen_data.get('numero')) and 
                                                    aen.get('descricao') == aen_data.get('descricao')):
                                                    if 'criterios_auditoria' not in aen:
                                                        aen['criterios_auditoria'] = []
                                                    if criterio not in aen['criterios_auditoria']:
                                                        aen['criterios_auditoria'].append(criterio)
                                                        save_objetivos_navais_data(data, self.json_file_path)
                                                    break
                        
                        event.accept()
                        return
            
            event.ignore()

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #44475a;
            }
            QListWidget::item:hover {
                background-color: #44475a;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(item.text())
                drag.setMimeData(mime_data)
                drag.exec(Qt.DropAction.MoveAction)
        else:
            super().mousePressEvent(event)

