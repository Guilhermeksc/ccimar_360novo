from PyQt6.QtWidgets import (QTreeView, QListWidget)
from PyQt6.QtGui import  QStandardItem, QDrag, QFont
from PyQt6.QtCore import Qt, QMimeData
import json
from .criterio_widget import CriterioWidget
from .json_utils import load_objetivos_navais_data, save_objetivos_navais_data
import re
def get_treeview_stylesheet():
    return """
        QTreeView {
            background-color: transparent;
            color: #FFF;
            font-size: 20px;
            border: 1px solid #25283D;
        }
        /* Perspectivas */
        QTreeView::item:!has-siblings:!has-children,
        QTreeView::branch:!has-siblings:!has-children {
            color: #8AB4F7;  /* Azul principal */
        }
        /* OBNAV */
        QTreeView::item:has-siblings:!has-children,
        QTreeView::branch:has-siblings:!has-children {
            font-size: 12px;
            color: #4C8BF5;  /* Azul mais escuro */
        }
        /* EN */
        QTreeView::item:has-siblings:has-children,
        QTreeView::branch:has-siblings:has-children {
            color: #B6D4FF;  /* Azul mais claro */
        }
        /* AEN */
        QTreeView::item:has-children,
        QTreeView::branch:has-children {
            color: #63A1FF;  /* Azul médio */
        }
        /* Critérios */
        QTreeView::item,
        QTreeView::branch {
            color: #E8F1FF;
            font-style: italic;
            font-family: "Courier New";
        }
        QTreeView::item:selected {
            background-color: #3B71CA;  /* Azul escuro para seleção */
        }
        QTreeView::item:hover {
            background-color: #1E3A8A;  /* Azul muito escuro para hover */
        }
    """        
class CustomTreeView(QTreeView):
    def __init__(self, icons=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Habilita drops
        self.json_file_path = None
        self.update_callback = None
        self.setStyleSheet(get_treeview_stylesheet())  # Aplica o estilo separado

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

    def add_criterios_ordenados(self, parent_item, criterios):
        """Adiciona critérios ao TreeView, garantindo a ordenação correta."""
        
        def extract_number(text):
            """Extrai o número inicial da string, se houver, para ordenação numérica."""
            match = re.match(r"(\d+)", text)
            return int(match.group(1)) if match else float('inf')  # Inf coloca strings puras no final

        # Ordena os critérios do menor para o maior
        criterios.sort(key=extract_number)

        # Remove todos os critérios visuais antes de reinseri-los
        for i in reversed(range(parent_item.rowCount())):
            parent_item.removeRow(i)

        # Insere os critérios ordenados
        for criterio in criterios:
            criterio_item = QStandardItem()
            criterio_item.setEditable(False)
            criterio_item.setData(f"criterio: {criterio}", Qt.ItemDataRole.UserRole)
            criterio_item.setText("")  # Define texto vazio para evitar sobreposição
            
            # Cria e define o widget personalizado para o critério
            widget = CriterioWidget(
                criterio,
                lambda item=criterio_item: self.remove_criterio(item)
            )
            
            parent_item.appendRow(criterio_item)
            self.setIndexWidget(criterio_item.index(), widget)

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
            criterio = event.mimeData().text().strip()
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

                    # Verifica se o critério já existe na AEN para evitar duplicação
                    if criterio not in aen_data['criterios_auditoria']:
                        aen_data['criterios_auditoria'].append(criterio)

                        # Ordena os critérios corretamente do menor para o maior
                        def extract_number(text):
                            """Extrai o número inicial da string, se houver, para ordenação numérica."""
                            match = re.match(r"(\d+)", text)
                            return int(match.group(1)) if match else float('inf')  # Inf garante que texto puro vá para o final

                        aen_data['criterios_auditoria'].sort(key=extract_number)

                        self.add_criterios_ordenados(item, aen_data['criterios_auditoria'])

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
                                                        aen['criterios_auditoria'].sort(key=extract_number)
                                                        save_objetivos_navais_data(data, self.json_file_path)
                                                    break

                        if self.update_callback:
                            self.update_callback()
                        event.accept()
                        return

            event.ignore()

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.OpenHandCursor)  # Define o cursor de mão aberta
        self.setStyleSheet(get_draggable_list_style())  # Aplica o estilo separado

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)  # Mantém o cursor fechado enquanto arrasta
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(item.text())
                drag.setMimeData(mime_data)
                drag.exec(Qt.DropAction.MoveAction)
                self.setCursor(Qt.CursorShape.OpenHandCursor)  # Retorna para mão aberta após soltar
        else:
            super().mouseMoveEvent(event)


def get_draggable_list_style():
    return """
        QListWidget {
            background-color: #181928;  /* Fundo similar ao TableView */
            color: white;  /* Texto branco */
            border: 1px solid #25283D;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #25283D;  /* Linha separadora sutil */
        }
        QListWidget::item:hover {
            background-color: #5568E8;  /* Azul vibrante ao passar o mouse */
            color: white;
        }
        QListWidget::item:selected {
            background-color: #3A57D2;  /* Azul escuro da seleção */
            color: white;
        }
    """

