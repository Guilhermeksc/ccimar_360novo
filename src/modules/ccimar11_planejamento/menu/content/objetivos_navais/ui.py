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
from .json_utils import load_objetivos_navais_data, save_objetivos_navais_data
from .objetivos_treeview import TreeLevelDelegate, CustomTreeView, DraggableListWidget
from .criterio_widget import CriterioWidget
from paths import CONFIG_PAINT_PATH
import re

def create_header_layout(icons):
    # Layout para ícones
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    icon_label = QLabel()
    icon_label.setPixmap(icons["marinha"].pixmap(40, 40))
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    """Cria o layout do cabeçalho com os ícones e títulos alinhados."""
    pem_label = QLabel("PEM 2040    ")
    pem_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")

    header_layout.addStretch()
    header_layout.addWidget(pem_label)
    header_layout.addWidget(icon_label)

    return header_layout

def get_treeview_stylesheet():
    return """
        QTreeView {
            background-color: transparent;
            font-size: 16px;
            color: #FFFFFF;
            border-radius: 4px;
            border: 1px solid #25283D;
        }
        QTreeView::item {
            /* Tenta forçar a quebra de linha, se suportado */
            white-space: normal;
        }
        QTreeView::item:selected {
            background-color: #3B71CA;
        }
        QTreeView::item:hover {
            background-color: #1E3A8A;
        }
    """
    
def create_objetivos_navais(title_text, icons, json_file_path=None):
    icons = icons
    # Frame principal
    content_frame = QFrame()

    main_layout = QVBoxLayout(content_frame)
    main_layout.setContentsMargins(5, 5, 5, 5)
    main_layout.setSpacing(2)
    
    # Adicionando o cabeçalho
    header_layout = create_header_layout(icons)
    main_layout.addLayout(header_layout)

    content_layout = QHBoxLayout()      
    # Lado esquerdo
    treeview_frame = QFrame()
    treeview_layout = QVBoxLayout(treeview_frame)
    treeview_layout.setContentsMargins(0, 0, 0, 0)
    treeview_layout.setSpacing(0)

    # Criação do TreeView
    tree = CustomTreeView(icons=icons)
    tree.setStyleSheet(get_treeview_stylesheet())

    tree.setItemDelegate(TreeLevelDelegate(tree))
    tree.setHeaderHidden(True)
    model = QStandardItemModel()
    tree.setModel(model)  # Definindo o modelo antes de qualquer atualização
    
    def update_tree_view():
        model.clear()
        data = load_objetivos_navais_data(json_file_path) if json_file_path else None
        def extract_number(text):
            """Extrai o número inicial da string, se houver, para ordenação numérica."""
            match = re.match(r"(\d+)", text)
            return int(match.group(1)) if match else float('inf')  # Inf coloca strings puras no final
        
        if data:
            # print("[DEBUG] Dados JSON carregados com sucesso")
            for perspectiva in data.get('perspectivas', []):
                # print(f"[DEBUG] Processando perspectiva: {perspectiva['nome']}")
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
                        en_item = QStandardItem(f"EN {en['numero']} - {en['titulo']}")
                        en_item.setEditable(False)
                        en_item.setData(en, Qt.ItemDataRole.UserRole)
                        obnav_item.appendRow(en_item)  # Adiciona o EN imediatamente
                        
                        for aen in en.get('acoes_estrategicas', []):
                            aen_item = QStandardItem(f"AEN {aen['numero']} - {aen['titulo']}")
                            aen_item.setEditable(False)
                            aen_item.setData(aen, Qt.ItemDataRole.UserRole)
                            en_item.appendRow(aen_item)  # Adiciona a AEN imediatamente

                            # Ordenar os critérios antes de adicionar ao TreeView
                            criterios_ordenados = sorted(aen.get('criterios_auditoria', []), key=extract_number)
                     
                            for criterio in criterios_ordenados:
                                criterio_item = QStandardItem()
                                criterio_item.setEditable(False)
                                criterio_item.setData(f"criterio: {criterio}", Qt.ItemDataRole.UserRole)
                                criterio_item.setText("")  # Define texto vazio para evitar sobreposição
                                aen_item.appendRow(criterio_item)

                                # Cria e define o widget personalizado para o critério
                                widget = CriterioWidget(
                                    criterio,
                                    lambda item=criterio_item: tree.remove_criterio(item)
                                )
                                tree.setIndexWidget(criterio_item.index(), widget)
                                print(f"[DEBUG] Widget personalizado definido para critério: {criterio}")

        tree.expandAll()
    
    # Configura os callbacks antes de atualizar a view
    content_frame.remove_criterio = update_tree_view
    tree.json_file_path = json_file_path
    tree.update_callback = update_tree_view
    
    update_tree_view()
    acao_estrategica_naval_label = QLabel("Ação Estratégica Naval (AEN) vinculada ao PEM 2040")
    acao_estrategica_naval_label.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #25283D;
        padding: 8px;
        border-radius: 5px;
    """)

    treeview_layout.addWidget(acao_estrategica_naval_label)
    treeview_layout.addWidget(tree)
            
    # Lado direito com lista de critérios
    criterio_frame = QFrame()
    criterio_frame.setMaximumWidth(250)
    criterio_layout = QVBoxLayout(criterio_frame)

    objetivos_auditaveis_label = QLabel("Objetivos Auditáveis")
    objetivos_auditaveis_label.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #25283D;
        padding: 8px;
        border-radius: 5px;
    """)
        
    criterio_layout.setContentsMargins(0, 0, 0, 0)
    criterio_layout.setSpacing(0)        
    # Lista de critérios
    criterios_list = DraggableListWidget()
    criterios = carregar_criterios_do_json(CONFIG_PAINT_PATH)
    
    for criterio in criterios:
        item = QListWidgetItem(criterio)
        font = item.font()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
        item.setFont(font)
        criterios_list.addItem(item)
    
    criterio_layout.addWidget(objetivos_auditaveis_label)
    criterio_layout.addWidget(criterios_list)
    content_layout.addWidget(criterio_frame)
    content_layout.addWidget(treeview_frame)
    main_layout.addLayout(content_layout)

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
                    
    # Botões abaixo da TreeView
    buttons_layout = create_buttons_layout(content_frame, export_data, import_data)
    main_layout.addLayout(buttons_layout)
            
    return content_frame

def create_buttons_layout(content_frame, export_callback, import_callback):
    layout = QHBoxLayout()
    
    export_button = QPushButton("Exportar Excel")
    import_button = QPushButton("Importar Excel")
    
    export_button.clicked.connect(export_callback)
    import_button.clicked.connect(import_callback)
    
    layout.addWidget(export_button)
    layout.addWidget(import_button)
    layout.addStretch()
    
    return layout

def carregar_criterios_do_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        dados_json = json.load(file)

    objetos = dados_json.get('objetos_auditaveis', [])

    criterios = [f"{objeto['nr']} - {objeto['descricao']}" for objeto in objetos]

    return criterios

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
    Importa dados de uma planilha Excel para a estrutura JSON,
    garantindo que números inteiros não fiquem com sufixo .0
    e que valores decimais sejam preservados.
    """
    def remove_float_zeros(value):
        """Converte float inteiro (ex: 1.0) para string '1', mantendo decimais quando necessário."""
        if pd.isna(value):
            return None
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

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

            # Localiza ou cria OBNAV
            obnav_numero = remove_float_zeros(row['OBNAV_Numero'])
            obnav = next(
                (o for o in current_persp['obnavs']
                 if o['numero'] == obnav_numero),
                None
            )
            if not obnav:
                obnav = {
                    'numero': obnav_numero,
                    'descricao': row['OBNAV_Descricao'],
                    'criterios_auditoria': [],
                    'estrategias_navais': []
                }
                current_persp['obnavs'].append(obnav)

            # Adiciona critérios de auditoria ao OBNAV
            if pd.notna(row.get('Criterios_Auditoria')):
                criterios = [c.strip() for c in str(row['Criterios_Auditoria']).split(',') if c.strip()]
                for criterio in criterios:
                    if criterio not in obnav['criterios_auditoria']:
                        obnav['criterios_auditoria'].append(criterio)

            # Localiza ou cria EN
            en_numero = remove_float_zeros(row['EN_Numero'])
            en = next(
                (e for e in obnav['estrategias_navais']
                 if e['numero'] == en_numero),
                None
            )
            if not en:
                en = {
                    'numero': en_numero,
                    'titulo': row['EN_Titulo'],
                    'descricao': row['EN_Descricao'],
                    'acoes_estrategicas': []
                }
                obnav['estrategias_navais'].append(en)

            # Cria a AEN e adiciona em EN
            aen_numero = remove_float_zeros(row['AEN_Numero'])
            aen = {
                'numero': aen_numero,
                'titulo': row['AEN_Titulo'],
                'descricao': row['AEN_Descricao'],
                'responsavel': row['Responsável']
            }
            # Evita duplicados
            if aen not in en['acoes_estrategicas']:
                en['acoes_estrategicas'].append(aen)

        return data

    except Exception as e:
        print(f"Erro ao importar Excel: {e}")
        return None


# def import_from_excel(excel_path):
#     """
#     Importa dados de uma planilha Excel para a estrutura JSON,
#     considerando as novas colunas EN_Titulo, AEN_Titulo e Responsável.
#     """
#     try:
#         df = pd.read_excel(excel_path)
#         data = {'perspectivas': []}
#         perspectivas = {}

#         for _, row in df.iterrows():
#             persp_nome = row['Perspectiva']

#             # Adiciona nova perspectiva se não existir
#             if persp_nome not in perspectivas:
#                 perspectivas[persp_nome] = {
#                     'nome': persp_nome,
#                     'obnavs': []
#                 }
#                 data['perspectivas'].append(perspectivas[persp_nome])

#             current_persp = perspectivas[persp_nome]

#             # Localiza ou cria OBNAV
#             obnav = next(
#                 (o for o in current_persp['obnavs']
#                  if str(o['numero']) == str(row['OBNAV_Numero'])),
#                 None
#             )
#             if not obnav:
#                 obnav = {
#                     'numero': row['OBNAV_Numero'],
#                     'descricao': row['OBNAV_Descricao'],
#                     'criterios_auditoria': [],
#                     'estrategias_navais': []
#                 }
#                 current_persp['obnavs'].append(obnav)

#             # Adiciona critérios de auditoria ao OBNAV
#             if pd.notna(row.get('Criterios_Auditoria')):
#                 criterios = [c.strip() for c in str(row['Criterios_Auditoria']).split(',') if c.strip()]
#                 for criterio in criterios:
#                     if criterio not in obnav['criterios_auditoria']:
#                         obnav['criterios_auditoria'].append(criterio)

#             # Localiza ou cria EN
#             en = next(
#                 (e for e in obnav['estrategias_navais']
#                  if str(e['numero']) == str(row['EN_Numero'])),
#                 None
#             )
#             if not en:
#                 en = {
#                     'numero': row['EN_Numero'],
#                     'titulo': row['EN_Titulo'],
#                     'descricao': row['EN_Descricao'],
#                     'acoes_estrategicas': []
#                 }
#                 obnav['estrategias_navais'].append(en)

#             # Cria a AEN e adiciona em EN
#             aen = {
#                 'numero': row['AEN_Numero'],
#                 'titulo': row['AEN_Titulo'],
#                 'descricao': row['AEN_Descricao'],
#                 'responsavel': row['Responsável']
#             }
#             # Evita duplicados
#             if aen not in en['acoes_estrategicas']:
#                 en['acoes_estrategicas'].append(aen)

#         return data

#     except Exception as e:
#         print(f"Erro ao importar Excel: {e}")
#         return None