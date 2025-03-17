from PyQt6.QtWidgets import (QLabel, QFrame, QHBoxLayout, QVBoxLayout, QTreeView,
                          QDialog, QPushButton, QLineEdit, QComboBox, QMessageBox,
                          QFileDialog, QListWidget, QListWidgetItem, QWidget, QSizePolicy)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QDrag, QCursor
from PyQt6.QtCore import Qt, QMimeData, QTimer
import json
import time
import pandas as pd
import os
import subprocess
import sys
from .json_utils import load_objetivos_navais_data, save_objetivos_navais_data
from .objetivos_treeview import TreeLevelDelegate, CustomTreeView, DraggableListWidget
from .criterio_widget import CriterioWidget
from docxtpl import DocxTemplate
from paths import CONFIG_PAINT_PATH, OBJETIVOS_NAVAIS_PATH, TEMPLATE_RELATORIO_PATH
import re

def create_header_layout(icons):
    # Layout para ícones
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    icon_label = QLabel()
    icon_label.setPixmap(icons["marinha"].pixmap(40, 40))
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    """Cria o layout do cabeçalho com os ícones e títulos alinhados."""
    pem_label = QLabel("PEM 2040 - Plano Estratégico da Marinha   ")
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
        # Capturar a posição atual do scrollbar vertical
        scroll_value = tree.verticalScrollBar().value()

        # Salvar o estado de expansão
        expanded_items = {}
        def salvar_estado(index, caminho=''):
            item = model.itemFromIndex(index)
            if item:
                novo_caminho = caminho + '/' + item.text()
                if tree.isExpanded(index):
                    expanded_items[novo_caminho] = True
                for i in range(model.rowCount(index)):
                    salvar_estado(model.index(i, 0, index), novo_caminho)
        for i in range(model.rowCount()):
            salvar_estado(model.index(i, 0))
        
        model.clear()
        
        data = load_objetivos_navais_data(json_file_path) if json_file_path else None
        def extract_number(text):
            match = re.match(r"(\d+)", text)
            return int(match.group(1)) if match else float('inf')
        
        if data:
            for perspectiva in data.get('perspectivas', []):
                perspec_item = QStandardItem(perspectiva['nome'])
                perspec_item.setEditable(False)
                perspec_item.setData(perspectiva, Qt.ItemDataRole.UserRole)
                model.appendRow(perspec_item)
                
                for obnav in perspectiva.get('obnavs', []):
                    obnav_item = QStandardItem(f"OBNAV {obnav['numero']} - {obnav['descricao']}")
                    obnav_item.setEditable(False)
                    obnav_item.setData(obnav, Qt.ItemDataRole.UserRole)
                    perspec_item.appendRow(obnav_item)
                    
                    for en in obnav.get('estrategias_navais', []):
                        en_item = QStandardItem(f"EN {en['numero']} - {en['titulo']}")
                        en_item.setEditable(False)
                        en_item.setData(en, Qt.ItemDataRole.UserRole)
                        obnav_item.appendRow(en_item)
                        
                        for aen in en.get('acoes_estrategicas', []):
                            aen_item = QStandardItem(f"AEN {aen['numero']} - {aen['titulo']}")
                            aen_item.setEditable(False)
                            aen_item.setData(aen, Qt.ItemDataRole.UserRole)
                            en_item.appendRow(aen_item)

                            criterios_ordenados = sorted(aen.get('criterios_auditoria', []), key=extract_number)
                    
                            for criterio in criterios_ordenados:
                                criterio_item = QStandardItem()
                                criterio_item.setEditable(False)
                                criterio_item.setData(f"criterio: {criterio}", Qt.ItemDataRole.UserRole)
                                criterio_item.setText("")
                                aen_item.appendRow(criterio_item)

                                widget = CriterioWidget(
                                    criterio,
                                    lambda item=criterio_item: tree.remove_criterio(item)
                                )
                                tree.setIndexWidget(criterio_item.index(), widget)
                                print(f"[DEBUG] Widget personalizado definido para critério: {criterio}")

        def restaurar_estado(index, caminho=''):
            item = model.itemFromIndex(index)
            if item:
                novo_caminho = caminho + '/' + item.text()
                if novo_caminho in expanded_items:
                    tree.setExpanded(index, True)
                for i in range(model.rowCount(index)):
                    restaurar_estado(model.index(i, 0, index), novo_caminho)
        for i in range(model.rowCount()):
            restaurar_estado(model.index(i, 0))

        # Restaurar a posição do scrollbar após a atualização completa do widget
        QTimer.singleShot(0, lambda: tree.verticalScrollBar().setValue(scroll_value))

            
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
    criterio_frame.setMaximumWidth(280)
    criterio_layout = QVBoxLayout(criterio_frame)

    objetivos_auditaveis_label = QLabel("Objetos Auditáveis")
    objetivos_auditaveis_label.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #25283D;
        padding: 8px;
        border-radius: 5px;
    """)
        
    criterio_layout.setContentsMargins(0, 0, 0, 0)
    criterio_layout.setSpacing(5)        
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
    buttons_layout = create_buttons_layout(content_frame, export_data, import_data, lambda: show_rank_dialog(content_frame), generate_report)
    main_layout.addLayout(buttons_layout)
            
    return content_frame

def create_buttons_layout(content_frame, export_callback, import_callback, rank_callback, report_callback):
    layout = QHBoxLayout()
    
    button_style = """
        QPushButton {
            background-color: #181928;
            color: white;
            border: 1px solid #25283D;
            padding: 8px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #3A57D2;
            color: white;
        }
    """
    
    export_button = QPushButton("Exportar Excel")
    import_button = QPushButton("Importar Excel")
    rank_button = QPushButton("Rank")
    report_button = QPushButton("Relatório")
    
    for button in [export_button, import_button, rank_button, report_button]:
        button.setStyleSheet(button_style)
        button.setCursor(Qt.CursorShape.PointingHandCursor) 
        
    export_button.clicked.connect(export_callback)
    import_button.clicked.connect(import_callback)
    rank_button.clicked.connect(rank_callback)
    report_button.clicked.connect(report_callback)
    
    layout.addWidget(export_button)
    layout.addWidget(import_button)
    layout.addWidget(rank_button)
    layout.addWidget(report_button)
    layout.addStretch()
    
    return layout

def carregar_criterios_do_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        dados_json = json.load(file)
    
    objetos = dados_json.get('objetos_auditaveis', [])
    
    criterios = [f"{objeto['nr']} - {objeto['descricao']}" for objeto in objetos]
    
    return criterios

def contar_acoes_estrategicas_por_criterio():
    with open(OBJETIVOS_NAVAIS_PATH, 'r', encoding='utf-8') as file:
        objetivos_navais = json.load(file)
    
    contador_criterios = {}
    detalhes_criterios = {}
    
    for perspectiva in objetivos_navais.get("perspectivas", []):
        for obnav in perspectiva.get("obnavs", []):
            for estrategia in obnav.get("estrategias_navais", []):
                for acao in estrategia.get("acoes_estrategicas", []):
                    for criterio in acao.get("criterios_auditoria", []):
                        if criterio in contador_criterios:
                            contador_criterios[criterio] += 1
                            detalhes_criterios[criterio].append(f"AEN {acao['numero']} - {acao['titulo']}")
                        else:
                            contador_criterios[criterio] = 1
                            detalhes_criterios[criterio] = [f"AEN {acao['numero']} - {acao['titulo']}"]
    
    return contador_criterios, detalhes_criterios

def generate_report():
    folder_path = QFileDialog.getExistingDirectory(None, "Selecionar Pasta")
    if not folder_path:
        return
    
    report_path = os.path.abspath(os.path.join(folder_path, "relatorio"))
    os.makedirs(report_path, exist_ok=True)
    file_docx = os.path.abspath(os.path.join(report_path, "relatorio_objaud_x_aen.docx"))
    file_pdf = os.path.abspath(os.path.join(report_path, "relatorio_objaud_x_aen.pdf"))
    
    criterios_rank, detalhes_criterios = contar_acoes_estrategicas_por_criterio()
    
    ranking = []
    for idx, (criterio, quantidade) in enumerate(sorted(criterios_rank.items(), key=lambda x: x[1], reverse=True), start=1):
        ranking.append(f"{idx}º colocado - Objetivo Auditável {criterio} [{quantidade}]")
    
    criterios = carregar_criterios_do_json(CONFIG_PAINT_PATH)
    
    relacao = []
    for criterio in criterios:
        acoes = detalhes_criterios.get(criterio, [])
        if acoes:
            relacao.append(f"{criterio}\n" + "\n".join(f"- {acao}" for acao in acoes))
    
    doc = DocxTemplate(str(TEMPLATE_RELATORIO_PATH))
    context = {
        "ranking": "\n\n".join(ranking),
        "relacao": "\n\n".join(relacao)
    }
    doc.render(context)
    doc.save(file_docx)


    
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

def show_rank_dialog(parent):
    criterios = carregar_criterios_do_json(CONFIG_PAINT_PATH)
    criterios_rank, detalhes_criterios = contar_acoes_estrategicas_por_criterio()
    
    dialog = QDialog(parent)
    dialog.setWindowTitle("Ranking de Objetos Auditáveis")
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1E2E;
            color: #FFFFFF;
            border-radius: 8px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
        }
    """)
    
    layout = QVBoxLayout()
    title_label = QLabel("Objetos Auditáveis Rankeados")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    tree_view = QTreeView()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Objetos Auditáveis Rankeados"])
    
    sorted_criterios = sorted(criterios_rank.items(), key=lambda x: x[1], reverse=True)
    
    for criterio, rank_count in sorted_criterios:
        parent_item = QStandardItem(f"{criterio} [ {rank_count} ]")
        parent_item.setEditable(False)
        
        for detalhe in detalhes_criterios.get(criterio, []):
            child_item = QStandardItem(detalhe)
            child_item.setEditable(False)
            parent_item.appendRow(child_item)
        
        model.appendRow(parent_item)
    
    tree_view.setModel(model)
    tree_view.expandAll()
    tree_view.setHeaderHidden(False)
    
    close_button = QPushButton("Fechar")
    close_button.clicked.connect(dialog.close)
    
    layout.addWidget(title_label)
    layout.addWidget(tree_view)
    layout.addWidget(close_button)
    
    dialog.setLayout(layout)
    dialog.exec()
