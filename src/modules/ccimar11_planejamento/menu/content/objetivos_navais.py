from PyQt6.QtWidgets import (QLabel, QFrame, QHBoxLayout, QVBoxLayout, QTreeView,
                          QDialog, QPushButton, QLineEdit, QComboBox, QMessageBox,
                          QFileDialog, QListWidget, QListWidgetItem, QWidget, QSizePolicy)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QDrag, QCursor
from PyQt6.QtCore import Qt, QMimeData
import json
import os
import pandas as pd
import subprocess
import sys

class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_callback()

class CriterioWidget(QWidget):
    def __init__(self, criterio_text, delete_callback, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # Remove todas as margens
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)
        
        # Define o fundo como transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Botão de exclusão com tamanho reduzido
        delete_label = ClickableLabel()
        delete_label.setText("❌")  # Emoji X como ícone de exclusão
        delete_label.setStyleSheet("color: #ff5555; font-size: 10px; background: transparent; padding: 0px;")
        delete_label.setFixedWidth(15)  # Largura fixa para o botão de exclusão
        delete_label.clicked_callback = delete_callback
        
        # Label do texto do critério
        text_label = QLabel(criterio_text)
        text_label.setStyleSheet("color: #f8f8f2; background: transparent; padding: 0px;")
        
        layout.addWidget(delete_label)
        layout.addWidget(text_label, 1)  # O texto expande para ocupar o espaço disponível
        
        # Ajusta o tamanho do widget para ser o menor possível
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

class CustomTreeView(QTreeView):
    def __init__(self, icons=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Habilita drops
        self.json_file_path = None
        self.update_callback = None
        
        # Configuração do estilo para os critérios
        self.setStyleSheet("""
            QTreeView {
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

def load_objetivos_navais_data(json_file_path):
    """
    Carrega os dados do arquivo JSON contendo a estrutura dos objetivos navais.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return None

def create_objetivos_navais(title_text, database_model, icons=None, json_file_path=None):
    # Frame principal
    content_frame = QFrame()
    content_frame.setStyleSheet("""
        QFrame { 
            padding: 10px;
            border-radius: 8px;
        }
        QPushButton {
            background-color: #6272a4;
            color: #f8f8f2;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            margin: 2px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #7283b5;
        }
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
        }
        QToolButton:hover {
            background-color: #44475a;
            border-radius: 4px;
        }
    """)
    
    main_layout = QHBoxLayout(content_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(10)
    
    # Lado esquerdo
    left_frame = QFrame()
    left_layout = QVBoxLayout(left_frame)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(5)
    
    # Título
    title_label = QLabel(title_text or "PEM 2040")
    title_font = QFont("Arial Black", 20)
    title_label.setFont(title_font)
    title_label.setStyleSheet("color: #FFFFFF;")
    left_layout.addWidget(title_label)
    
    # Criação do TreeView
    tree = CustomTreeView(icons=icons)
    tree.setHeaderHidden(True)
    model = QStandardItemModel()
    tree.setModel(model)  # Definindo o modelo antes de qualquer atualização
    
    def update_tree_view():
        print("[DEBUG] Iniciando atualização da árvore")
        model.clear()
        data = load_objetivos_navais_data(json_file_path) if json_file_path else None
        
        if data:
            print("[DEBUG] Dados JSON carregados com sucesso")
            for perspectiva in data.get('perspectivas', []):
                print(f"[DEBUG] Processando perspectiva: {perspectiva['nome']}")
                perspec_item = QStandardItem(perspectiva['nome'])
                perspec_item.setEditable(False)
                perspec_item.setData(perspectiva, Qt.ItemDataRole.UserRole)
                model.appendRow(perspec_item)  # Adiciona a perspectiva imediatamente
                
                for obnav in perspectiva.get('obnavs', []):
                    obnav_item = QStandardItem(f"OBNAV {obnav['numero']} - {obnav['descricao']}")
                    obnav_item.setEditable(False)
                    obnav_item.setData(obnav, Qt.ItemDataRole.UserRole)
                    perspec_item.appendRow(obnav_item)  # Adiciona o OBNAV imediatamente
                    
                    for en in obnav.get('estrategias_navais', []):
                        en_item = QStandardItem(f"EN {en['numero']} - {en['descricao']}")
                        en_item.setEditable(False)
                        en_item.setData(en, Qt.ItemDataRole.UserRole)
                        obnav_item.appendRow(en_item)  # Adiciona o EN imediatamente
                        
                        for aen in en.get('acoes_estrategicas', []):
                            aen_item = QStandardItem(f"AEN {aen['numero']} - {aen['descricao']}")
                            aen_item.setEditable(False)
                            aen_item.setData(aen, Qt.ItemDataRole.UserRole)
                            en_item.appendRow(aen_item)  # Adiciona a AEN imediatamente
                            
                            # Adiciona os critérios de auditoria da AEN
                            for criterio in aen.get('criterios_auditoria', []):
                                print(f"[DEBUG] Processando critério: {criterio}")
                                # Cria o item do critério
                                criterio_item = QStandardItem()
                                criterio_item.setEditable(False)
                                criterio_item.setData(f"criterio: {criterio}", Qt.ItemDataRole.UserRole)
                                criterio_item.setText("")  # Define texto vazio para evitar sobreposição
                                aen_item.insertRow(0, criterio_item)
                                
                                # Cria e define o widget personalizado para o critério
                                widget = CriterioWidget(
                                    criterio,
                                    lambda item=criterio_item: tree.remove_criterio(item)
                                )
                                tree.setIndexWidget(criterio_item.index(), widget)
                                print(f"[DEBUG] Widget personalizado definido para critério: {criterio}")
        else:
            print("[DEBUG] Nenhum dado JSON encontrado, usando estrutura padrão")
            # Usa a estrutura padrão caso não haja dados do JSON
            perspectivas = {
                "Resultados para a Sociedade": list(range(1, 6)),
                "Processos": list(range(6, 11)),
                "Institucional": list(range(11, 13))
            }
            
            for perspec, obnavs in perspectivas.items():
                perspec_item = QStandardItem(perspec)
                perspec_item.setEditable(False)
                model.appendRow(perspec_item)  # Adiciona a perspectiva imediatamente
                
                for num in obnavs:
                    obnav_item = QStandardItem(f"OBNAV {num}")
                    obnav_item.setEditable(False)
                    perspec_item.appendRow(obnav_item)  # Adiciona o OBNAV imediatamente
                    
                    en_item = QStandardItem("EN - Estratégia Naval")
                    en_item.setEditable(False)
                    obnav_item.appendRow(en_item)  # Adiciona o EN imediatamente
                    
                    aen_item = QStandardItem("AEN - Ação Estratégica Naval")
                    aen_item.setEditable(False)
                    en_item.appendRow(aen_item)  # Adiciona a AEN imediatamente
        
        tree.expandAll()
        print("[DEBUG] Árvore expandida e atualização concluída")
    
    # Configura os callbacks antes de atualizar a view
    content_frame.remove_criterio = update_tree_view
    tree.json_file_path = json_file_path
    tree.update_callback = update_tree_view
    
    update_tree_view()
    left_layout.addWidget(tree)
    
    # Botões abaixo da TreeView
    buttons_layout = QHBoxLayout()
    
    # Botões de Importação/Exportação
    export_button = QPushButton("Exportar Excel")
    import_button = QPushButton("Importar Excel")
    
    buttons_layout.addWidget(export_button)
    buttons_layout.addWidget(import_button)
    buttons_layout.addStretch()
    
    left_layout.addLayout(buttons_layout)
    
    def export_data():
        if not json_file_path:
            QMessageBox.warning(content_frame, "Erro", "É necessário ter um arquivo JSON configurado.")
            return
        
        data = load_objetivos_navais_data(json_file_path)
        if not data:
            QMessageBox.warning(content_frame, "Erro", "Não foi possível carregar os dados para exportação.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            content_frame,
            "Exportar para Excel",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            if export_to_excel(data, file_path):
                reply = QMessageBox.question(
                    content_frame,
                    "Exportação Concluída",
                    "Dados exportados com sucesso. Deseja abrir o arquivo?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        os.startfile(file_path)
                    except:
                        subprocess.run(['xdg-open', file_path])
            else:
                QMessageBox.warning(content_frame, "Erro", "Erro ao exportar os dados.")
    
    def import_data():
        if not json_file_path:
            QMessageBox.warning(content_frame, "Erro", "É necessário ter um arquivo JSON configurado.")
            return
        
        reply = QMessageBox.question(
            content_frame,
            "Confirmar Importação",
            "A importação irá substituir todos os dados existentes. Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                content_frame,
                "Importar do Excel",
                "",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                data = import_from_excel(file_path)
                if data:
                    if save_objetivos_navais_data(data, json_file_path):
                        update_tree_view()
                        QMessageBox.information(content_frame, "Sucesso", "Dados importados com sucesso!")
                    else:
                        QMessageBox.warning(content_frame, "Erro", "Erro ao salvar os dados importados.")
                else:
                    QMessageBox.warning(content_frame, "Erro", "Erro ao importar os dados do Excel.")
    
    # Conecta os botões às funções
    export_button.clicked.connect(export_data)
    import_button.clicked.connect(import_data)
    
    main_layout.addWidget(left_frame)
    
    # Lado direito com lista de critérios
    right_frame = QFrame()
    right_frame.setStyleSheet("background-color: #333; border-radius: 8px;")
    right_frame.setMaximumWidth(250)
    right_layout = QVBoxLayout(right_frame)
    right_layout.setContentsMargins(10, 10, 10, 10)
    
    # Título dos critérios
    criterios_label = QLabel("Critérios de Auditoria")
    criterios_label.setStyleSheet("color: #FFF; font-size: 16px; margin-bottom: 10px;")
    right_layout.addWidget(criterios_label)
    
    # Lista de critérios
    criterios_list = DraggableListWidget()
    criterios = [
        "Execução/Licitação",
        "Pagamento",
        "Municiamento",
        "Patrimônio",
        "Última Auditoria"
    ]
    
    for criterio in criterios:
        item = QListWidgetItem(criterio)
        criterios_list.addItem(item)
    
    right_layout.addWidget(criterios_list)
    main_layout.addWidget(right_frame)
    
    return content_frame

def save_objetivos_navais_data(data, json_file_path):
    """
    Salva os dados no arquivo JSON.
    """
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")
        return False

def export_to_excel(data, output_path):
    """
    Exporta os dados do JSON para uma planilha Excel estruturada.
    """
    rows = []
    for perspectiva in data.get('perspectivas', []):
        persp_nome = perspectiva['nome']
        for obnav in perspectiva.get('obnavs', []):
            obnav_num = obnav['numero']
            obnav_desc = obnav['descricao']
            criterios = ', '.join(obnav.get('criterios_auditoria', []))
            
            for en in obnav.get('estrategias_navais', []):
                en_num = en['numero']
                en_desc = en['descricao']
                
                for aen in en.get('acoes_estrategicas', []):
                    rows.append({
                        'Perspectiva': persp_nome,
                        'OBNAV_Numero': obnav_num,
                        'OBNAV_Descricao': obnav_desc,
                        'Criterios_Auditoria': criterios,
                        'EN_Numero': en_num,
                        'EN_Descricao': en_desc,
                        'AEN_Numero': aen['numero'],
                        'AEN_Descricao': aen['descricao']
                    })
    
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
    return True

def import_from_excel(excel_path):
    """
    Importa dados de uma planilha Excel para a estrutura JSON.
    """
    try:
        df = pd.read_excel(excel_path)
        data = {'perspectivas': []}
        perspectivas = {}
        
        for _, row in df.iterrows():
            persp_nome = row['Perspectiva']
            
            # Adiciona nova perspectiva se não existir
            if persp_nome not in perspectivas:
                perspectivas[persp_nome] = {
                    'nome': persp_nome,
                    'obnavs': []
                }
                data['perspectivas'].append(perspectivas[persp_nome])
            
            current_persp = perspectivas[persp_nome]
            
            # Procura OBNAV existente ou cria novo
            obnav = next(
                (o for o in current_persp['obnavs'] if str(o['numero']) == str(row['OBNAV_Numero'])),
                None
            )
            if not obnav:
                obnav = {
                    'numero': row['OBNAV_Numero'],
                    'descricao': row['OBNAV_Descricao'],
                    'criterios_auditoria': [],
                    'estrategias_navais': []
                }
                current_persp['obnavs'].append(obnav)
            
            # Adiciona critérios de auditoria
            if pd.notna(row.get('Criterios_Auditoria')):
                criterios = [c.strip() for c in str(row['Criterios_Auditoria']).split(',') if c.strip()]
                for criterio in criterios:
                    if criterio not in obnav['criterios_auditoria']:
                        obnav['criterios_auditoria'].append(criterio)
            
            # Procura EN existente ou cria novo
            en = next(
                (e for e in obnav['estrategias_navais'] if str(e['numero']) == str(row['EN_Numero'])),
                None
            )
            if not en:
                en = {
                    'numero': row['EN_Numero'],
                    'descricao': row['EN_Descricao'],
                    'acoes_estrategicas': []
                }
                obnav['estrategias_navais'].append(en)
            
            # Adiciona AEN
            aen = {
                'numero': row['AEN_Numero'],
                'descricao': row['AEN_Descricao']
            }
            if aen not in en['acoes_estrategicas']:
                en['acoes_estrategicas'].append(aen)
        
        return data
    except Exception as e:
        print(f"Erro ao importar Excel: {e}")
        return None