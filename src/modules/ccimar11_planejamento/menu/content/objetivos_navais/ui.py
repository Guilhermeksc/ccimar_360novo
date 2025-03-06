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
from paths import OBJETIVOS_NAVAIS_PATH
from .json_utils import load_objetivos_navais_data, save_objetivos_navais_data
from .objetivos_treeview import CustomTreeView, DraggableListWidget
from .criterio_widget import CriterioWidget

def create_objetivos_navais(title_text, icons, json_file_path=None):
    icons = icons
    # Frame principal
    content_frame = QFrame()

    main_layout = QVBoxLayout(content_frame)
    main_layout.setContentsMargins(5, 5, 5, 5)
    main_layout.setSpacing(2)
    title_layout = QHBoxLayout()
    # Layout vertical para os títulos
    title_text_layout = QVBoxLayout()
    pem_label = QLabel("PEM 2040")
    pem_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFFFFF;")
    plano_label = QLabel("Plano Estratégico da Marinha")
    plano_label.setStyleSheet("font-size: 18px; color: #FFFFFF;")
    title_text_layout.addWidget(pem_label)
    title_text_layout.addWidget(plano_label)
    title_text_layout.setSpacing(2)
    title_text_layout.setContentsMargins(0, 0, 0, 0)

    icon_label = QLabel()
    icon_label.setPixmap(icons["marinha"].pixmap(60, 60))  # Define o ícone com tamanho 50x50
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    acanto_label = QLabel()
    acanto_label.setPixmap(icons["acanto"].pixmap(120, 60))  # Define o ícone com tamanho 50x50
    acanto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    title_layout.addWidget(icon_label)
    title_layout.addLayout(title_text_layout)
    title_layout.addStretch()
    title_layout.addWidget(acanto_label)

    main_layout.addLayout(title_layout)


    content_layout = QHBoxLayout()      
    # Lado esquerdo
    treeview_frame = QFrame()
    treeview_layout = QVBoxLayout(treeview_frame)
    treeview_layout.setContentsMargins(0, 0, 0, 0)
    treeview_layout.setSpacing(5)

    # Criação do TreeView
    tree = CustomTreeView(icons=icons)
    tree.setHeaderHidden(True)
    model = QStandardItemModel()
    tree.setModel(model)  # Definindo o modelo antes de qualquer atualização
    
    def update_tree_view():
        model.clear()
        data = load_objetivos_navais_data(json_file_path) if json_file_path else None
        
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
                                # print(f"[DEBUG] Processando critério: {criterio}")
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
        # print("[DEBUG] Árvore expandida e atualização concluída")
    
    # Configura os callbacks antes de atualizar a view
    content_frame.remove_criterio = update_tree_view
    tree.json_file_path = json_file_path
    tree.update_callback = update_tree_view
    
    update_tree_view()
    treeview_layout.addWidget(tree)
    
    # Botões abaixo da TreeView
    buttons_layout = QHBoxLayout()
    
    # Botões de Importação/Exportação
    export_button = QPushButton("Exportar Excel")
    import_button = QPushButton("Importar Excel")
    
    buttons_layout.addWidget(export_button)
    buttons_layout.addWidget(import_button)
    buttons_layout.addStretch()
    
    treeview_layout.addLayout(buttons_layout)
    
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
    

    
    # Lado direito com lista de critérios
    criterio_frame = QFrame()
    criterio_frame.setMaximumWidth(250)
    criterio_layout = QVBoxLayout(criterio_frame)
    criterio_layout.setContentsMargins(10, 10, 10, 10)
        
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
    
    criterio_layout.addWidget(criterios_list)
    content_layout.addWidget(criterio_frame)
    content_layout.addWidget(treeview_frame)
    main_layout.addLayout(content_layout)
    
    return content_frame

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