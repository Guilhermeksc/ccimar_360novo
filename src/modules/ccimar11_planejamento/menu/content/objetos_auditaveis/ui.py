import os
import json
import pandas as pd
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QStyledItemDelegate,
    QGroupBox, QTableWidget, QTableWidgetItem, QScrollArea, QWidget,
    QSizePolicy, QDialog, QComboBox, QFormLayout, QTabWidget, QDialogButtonBox,
    QSpinBox, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt
from paths import CONFIG_PAINT_PATH
from .tableview import RiscoDelegate, CustomTableView, ExcelModelManager, load_config
from .multiplicadores import MultiplicadoresDialog
from utils.styles.style_add_button import apply_button_style
from utils.styles.style_table import apply_table_style
from .edit_dialog import EditDialog

def create_objetos_auditaveis(title_text):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Barra de título e botões
    title_layout = QHBoxLayout()
    title_label = QLabel("ANEXO 'A' CCIMAR 10-02")
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()

    btn_export = QPushButton("Exportar")
    apply_button_style(btn_export)
    title_layout.addWidget(btn_export)

    btn_import = QPushButton("Importar")
    apply_button_style(btn_import)
    title_layout.addWidget(btn_import)

    def open_riscos_dialog():
        # Carrega a configuração atual
        config = load_config()
        current_riscos = config.get("riscos", {
            "Muito Alto": 250,
            "Alto": 200,
            "Médio": 150,
            "Baixo": 100,
            "Muito Baixo": 50
        })
        
        # Cria o QDialog para edição dos riscos com o style sheet compatível
        dialog = QDialog(main_frame)
        dialog.setWindowTitle("Editar Riscos")
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
            QSpinBox {
                background-color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton[text="Cancelar"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #e53935;
            }
        """)
        
        layout = QFormLayout(dialog)
        
        # Cria QSpinBoxes para cada risco
        spin_muito_alto = QSpinBox()
        spin_alto = QSpinBox()
        spin_medio = QSpinBox()
        spin_baixo = QSpinBox()
        spin_muito_baixo = QSpinBox()
        
        # Define um intervalo razoável para os valores (0 a 1000)
        for spin in [spin_muito_alto, spin_alto, spin_medio, spin_baixo, spin_muito_baixo]:
            spin.setRange(0, 1000)
        
        # Define os valores iniciais a partir da configuração atual
        spin_muito_alto.setValue(current_riscos.get("Muito Alto", 250))
        spin_alto.setValue(current_riscos.get("Alto", 200))
        spin_medio.setValue(current_riscos.get("Médio", 150))
        spin_baixo.setValue(current_riscos.get("Baixo", 100))
        spin_muito_baixo.setValue(current_riscos.get("Muito Baixo", 50))
        
        # Adiciona os campos ao formulário
        layout.addRow("Muito Alto:", spin_muito_alto)
        layout.addRow("Alto:", spin_alto)
        layout.addRow("Médio:", spin_medio)
        layout.addRow("Baixo:", spin_baixo)
        layout.addRow("Muito Baixo:", spin_muito_baixo)
        
        # Função para atualizar as restrições de modo que:
        # Muito Alto > Alto > Médio > Baixo > Muito Baixo
        def update_constraints():
            spin_alto.setMaximum(spin_muito_alto.value() - 1)
            spin_medio.setMaximum(spin_alto.value() - 1)
            spin_baixo.setMaximum(spin_medio.value() - 1)
            spin_muito_baixo.setMaximum(spin_baixo.value() - 1)
        
        # Conecta a alteração de valor de cada spinbox à atualização das restrições
        spin_muito_alto.valueChanged.connect(update_constraints)
        spin_alto.valueChanged.connect(update_constraints)
        spin_medio.valueChanged.connect(update_constraints)
        spin_baixo.valueChanged.connect(update_constraints)
        update_constraints()
        
        # Botões de "Salvar" e "Cancelar"
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(button_box)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Atualiza os valores de riscos
            new_riscos = {
                "Muito Alto": spin_muito_alto.value(),
                "Alto": spin_alto.value(),
                "Médio": spin_medio.value(),
                "Baixo": spin_baixo.value(),
                "Muito Baixo": spin_muito_baixo.value()
            }
            config["riscos"] = new_riscos
            try:
                with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                QMessageBox.information(main_frame, "Sucesso", "Configuração de riscos salva com sucesso!")
                load_model_from_config()  # Atualiza o TableView com os novos valores
            except Exception as e:
                QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar a configuração de riscos: {e}")

    # Configura o botão "Riscos" para abrir o diálogo
    btn_riscos = QPushButton("Riscos")
    apply_button_style(btn_riscos)
    title_layout.addWidget(btn_riscos)
    btn_riscos.clicked.connect(open_riscos_dialog)

    def open_multiplicadores_dialog():
        dialog = MultiplicadoresDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            load_model_from_config()  # Recarrega a tabela após salvar

    btn_multiplicadores = QPushButton("Multiplicadores")
    apply_button_style(btn_multiplicadores)
    title_layout.addWidget(btn_multiplicadores)
    btn_multiplicadores.clicked.connect(open_multiplicadores_dialog)

    # Botão de full screen para o mapa (table_view)
    btn_fullscreen = QPushButton("Mapa Full Screen")
    apply_button_style(btn_fullscreen)
    title_layout.addWidget(btn_fullscreen)

    def open_fullscreen_tableview():
        main_layout.removeWidget(table_view)
        table_view.setParent(None)
        
        fullscreen_dialog = QDialog()
        fullscreen_dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        dialog_layout = QVBoxLayout(fullscreen_dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(table_view)
        
        def close_fullscreen():
            fullscreen_dialog.close()
            table_view.setParent(main_frame)
            main_layout.insertWidget(1, table_view)  # reinserir na posição original
        
        close_button = QPushButton("X", fullscreen_dialog)
        close_button.setFixedSize(40, 40)
        close_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 150);
                color: red;
                font-size: 24px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 150);
                color: white;
            }
        """)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(close_fullscreen)
        close_button.raise_()
        
        def on_resize(event):
            close_button.move(fullscreen_dialog.width() - close_button.width() - 10, 10)
            return QDialog.resizeEvent(fullscreen_dialog, event)
        fullscreen_dialog.resizeEvent = on_resize
        
        def on_key_press(event):
            if event.key() == Qt.Key.Key_Escape:
                close_fullscreen()
            else:
                return QDialog.keyPressEvent(fullscreen_dialog, event)
        fullscreen_dialog.keyPressEvent = on_key_press
        
        fullscreen_dialog.showFullScreen()

    btn_fullscreen.clicked.connect(open_fullscreen_tableview)

    # Botão de full screen para os Critérios (criteria_container)
    btn_crit_fullscreen = QPushButton("Critérios Full Screen")
    apply_button_style(btn_crit_fullscreen)

    title_layout.addWidget(btn_crit_fullscreen)

    def open_fullscreen_criteria():
        # Armazena as alturas fixas originais dos QGroupBox dentro do criteria_container
        original_heights = {}
        for group_box in criteria_container.findChildren(QGroupBox):
            original_heights[group_box] = group_box.height()
            # Remove a limitação de altura
            group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            group_box.setMinimumHeight(0)
            group_box.setMaximumHeight(16777215)
        
        # Armazena o style sheet original do criteria_container
        original_container_style = criteria_container.styleSheet()
        # Ajusta o plano de fundo para a cor #181928
        criteria_container.setStyleSheet("background-color: #181928;")
        
        # Remove o container de critérios do layout original
        main_layout.removeWidget(criteria_container)
        criteria_container.setParent(None)
        
        # Cria a janela full screen sem pai
        fullscreen_dialog = QDialog()
        fullscreen_dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        dialog_layout = QVBoxLayout(fullscreen_dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(criteria_container)
        
        # Função para fechar a janela e restaurar as configurações originais
        def close_fullscreen():
            fullscreen_dialog.close()
            criteria_container.setParent(main_frame)
            main_layout.insertWidget(2, criteria_container)  # ajuste o índice conforme necessário
            
            # Restaura a altura fixa original para cada QGroupBox
            for group_box in criteria_container.findChildren(QGroupBox):
                original_height = original_heights.get(group_box, 300)
                group_box.setFixedHeight(original_height)
            # Restaura o style sheet original do container
            criteria_container.setStyleSheet(original_container_style)
        
        # Botão "X" com fundo preto transparente, efeito hover e cursor pointer
        close_button = QPushButton("X", fullscreen_dialog)
        close_button.setFixedSize(40, 40)
        close_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 150);
                color: red;
                font-size: 24px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 150);
                color: white;
            }
        """)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(close_fullscreen)
        close_button.raise_()  # Garante que o botão fique sobre o conteúdo
        
        # Reposiciona o botão "X" no canto superior direito durante o redimensionamento
        def on_resize(event):
            close_button.move(fullscreen_dialog.width() - close_button.width() - 10, 10)
            return QDialog.resizeEvent(fullscreen_dialog, event)
        fullscreen_dialog.resizeEvent = on_resize
        
        # Captura a tecla ESC para fechar a janela full screen
        def on_key_press(event):
            if event.key() == Qt.Key.Key_Escape:
                close_fullscreen()
            else:
                return QDialog.keyPressEvent(fullscreen_dialog, event)
        fullscreen_dialog.keyPressEvent = on_key_press
        
        fullscreen_dialog.showFullScreen()


    btn_crit_fullscreen.clicked.connect(open_fullscreen_criteria)
   
    main_layout.addLayout(title_layout)

    # Tabela principal (CustomTableView)
    table_view = CustomTableView()
    table_view.setFont(QFont("Arial", 12))  # Define fonte maior para melhor visibilidade

    apply_table_style(table_view)

    model = QStandardItemModel()
    table_view.setModel(model)
    headers = ["NR", "Objetos Auditáveis", "Materialidade", "Relevância", "Criticidade", "Total", "Risco"]
    model.setHorizontalHeaderLabels(headers)
    
    # Aplicar o delegate para colorir as células de risco
    risco_delegate = RiscoDelegate()
    table_view.setItemDelegateForColumn(6, risco_delegate)
    
    # Centraliza os cabeçalhos da tabela principal
    for col in range(len(headers)):
        header_item = model.horizontalHeaderItem(col)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    table_view.verticalHeader().setDefaultSectionSize(30)
    main_layout.addWidget(table_view)

    def format_value(value):
        return str(int(value)) if value == int(value) else str(value)

    def load_model_from_config():
        config = load_config()
        model.clear()
        
        if not config:
            return

        risco_dict = config.get("riscos", {
            "Muito Alto": 250,
            "Alto": 200,
            "Médio": 150,
            "Baixo": 100,
            "Muito Baixo": 50
        })
        
        # Ordena os riscos por threshold decrescente
        sorted_riscos = sorted(risco_dict.items(), key=lambda x: x[1], reverse=True)

        # Obter os multiplicadores do JSON
        multiplicadores = config.get("multiplicador", {
            "materialidade": 4,
            "relevancia": 2,
            "criticidade": 4
        })

        # Definir os cabeçalhos dinâmicos com os multiplicadores
        headers = [
            "NR", 
            "Objetos Auditáveis", 
            f"Materialidade\n(x{multiplicadores.get('materialidade', 4)})", 
            f"Relevância\n(x{multiplicadores.get('relevancia', 2)})", 
            f"Criticidade\n(x{multiplicadores.get('criticidade', 4)})", 
            "Total", 
            "Risco"
        ]
        
        model.setHorizontalHeaderLabels(headers)

        for item in config.get("objetos_auditaveis", []):
            nr = item.get("nr", "")
            descricao = item.get("descricao", "")

            # Calcular os valores considerando os multiplicadores
            mat_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 for v in item.get("materialidade", {}).values())
            rel_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 for v in item.get("relevancia", {}).values())
            crit_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 for v in item.get("criticidade", {}).values())

            # Aplicar multiplicadores
            mat_val = mat_val_raw * multiplicadores.get("materialidade", 4)
            rel_val = rel_val_raw * multiplicadores.get("relevancia", 2)
            crit_val = crit_val_raw * multiplicadores.get("criticidade", 4)

            # Calcular o total
            total = mat_val + rel_val + crit_val

            # Determinar o risco com base no total usando os rótulos obtidos do JSON
            risco = item.get("risco", "")
            if not risco:
                for label, threshold in sorted_riscos:
                    if total >= threshold:
                        risco = label
                        break
                else:
                    risco = sorted_riscos[-1][0]

            row = [
                QStandardItem(str(nr)),
                QStandardItem(str(descricao)),
                QStandardItem(format_value(mat_val)),
                QStandardItem(format_value(rel_val)),
                QStandardItem(format_value(crit_val)),
                QStandardItem(format_value(total)),
                QStandardItem(str(risco))
            ]
            
            for cell in row:
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            model.appendRow(row)

        # Ajuste do tamanho das colunas
        table_view.setColumnWidth(0, 50)
        table_view.setColumnWidth(2, 110)
        table_view.setColumnWidth(3, 100)
        table_view.setColumnWidth(4, 100)
        table_view.setColumnWidth(5, 100)
        table_view.setColumnWidth(6, 100)
        table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    load_model_from_config()

    def update_json_from_table():
        config = load_config()
        if not config:
            return

        objetos_auditaveis = config.get("objetos_auditaveis", [])
        multiplicadores = config.get("multiplicador", {
            "materialidade": 4,
            "relevancia": 2,
            "criticidade": 4
        })

        # Recalcula os totais e o risco de cada objeto auditável
        for obj in objetos_auditaveis:
            # Soma os valores de cada critério (assumindo que cada valor já foi atualizado via critérios filhos)
            mat_val_raw = sum(v.get("valor", 0) for v in obj.get("materialidade", {}).values())
            rel_val_raw = sum(v.get("valor", 0) for v in obj.get("relevancia", {}).values())
            crit_val_raw = sum(v.get("valor", 0) for v in obj.get("criticidade", {}).values())

            # Aplica os multiplicadores
            mat_val = mat_val_raw * multiplicadores.get("materialidade", 4)
            rel_val = rel_val_raw * multiplicadores.get("relevancia", 2)
            crit_val = crit_val_raw * multiplicadores.get("criticidade", 4)
            total = mat_val + rel_val + crit_val
            obj["total"] = total

        config["objetos_auditaveis"] = objetos_auditaveis

        try:
            with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("Arquivo JSON atualizado com sucesso.")
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Falha ao salvar no JSON: {e}")

        # Atualiza o modelo do table_view com os novos valores
        load_model_from_config()

    # Conectar evento de alteração dos dados na tabela
    model.dataChanged.connect(update_json_from_table)

    # Container para os 3 QGroupBox, com altura fixa
    criteria_container = QFrame()
    criteria_layout = QHBoxLayout(criteria_container)

    def adjust_table_size(table_widget: QTableWidget):
        """
        Ajusta a altura do QTableWidget para exibir todas as linhas sem scroll interno.
        Assim, se houver muitas linhas, o QScrollArea do GroupBox fará a rolagem.
        Considera também a quebra de linha nas células.
        """
        # Primeiro, ajusta as linhas para acomodar o conteúdo com quebra de linha
        table_widget.resizeRowsToContents()
        table_widget.resizeColumnsToContents()

        # Calcula a altura total (cabeçalho horizontal + altura de cada linha + margens)
        total_height = table_widget.horizontalHeader().height()
        for row_idx in range(table_widget.rowCount()):
            total_height += table_widget.rowHeight(row_idx)

        # Margem para o frame e possíveis bordas
        total_height += 4
        table_widget.setFixedHeight(total_height)

    def update_criteria_groupboxes():
        while criteria_layout.count():
            item = criteria_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        config = load_config()
        if not config:
            return

        pontuacao = config.get("pontuacao_criterios", {})
        for category in ["materialidade", "relevancia", "criticidade"]:
            group_box = QGroupBox(category.capitalize())
            group_box.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            )
            
            group_box.setFixedHeight(300)

            # Aplicando um efeito ao GroupBox para combinar com #181928
            group_box.setStyleSheet("""
                QGroupBox {
                    background-color: #181928;  /* Fundo escuro */
                    border: 2px solid #25283D;  /* Borda sutil */
                    border-radius: 8px;  /* Bordas arredondadas */
                    margin-top: 20px;  /* Ajuste para o título não sobrepor a borda */
                    padding: 10px;
                    font-size: 16px;
                    font-weight: bold;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px 10px;
                    background-color: #25283D; /* Fundo do título */
                    color: white;                    
                    border-radius: 4px;
                }
            """)


            # Layout vertical para o conteúdo dentro do groupbox
            group_layout = QVBoxLayout(group_box)
            group_layout.setContentsMargins(2, 12, 2, 2)  # Aumentar a margem superior para dar espaço ao título
            group_layout.setSpacing(0)  # Reduzir o espaçamento para empurrar o conteúdo para cima
            # Configurar o alinhamento do layout do grupo para o topo
            group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Cria um QScrollArea para rolar o conteúdo se exceder a altura do groupbox
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            # Configurar a política de tamanho para que o scroll area ocupe todo o espaço disponível
            scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # Definir o alinhamento do scroll area para o topo
            scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
            # Remover a borda do scroll area para melhor aparência
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)

            # Widget interno do scroll
            content_widget = QWidget()
            # Define o background do content_widget para preto
            content_widget.setStyleSheet("background-color: #181928;")
            # Configurar a política de tamanho para que o widget de conteúdo ocupe todo o espaço disponível
            content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(1)  # Reduzir ainda mais o espaçamento
            # Configurar o alinhamento para o topo
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            # Reduzir as margens para empurrar o conteúdo para cima
            content_layout.setContentsMargins(0, 0, 0, 0)

            # Lista para armazenar referências aos labels para ajustar largura posteriormente
            title_labels = []
            
            # Função para ajustar a largura dos labels quando o container for redimensionado
            def adjust_labels_width():
                for label in title_labels:
                    label.setMaximumWidth(content_widget.width() - 10)  # -10 para margem
            
            # Conectar o evento de redimensionamento
            content_widget.resizeEvent = lambda event: adjust_labels_width()

            criteria_list = pontuacao.get(category, [])
            for idx, crit in enumerate(criteria_list):
                # Se não for o primeiro critério, adicione um pequeno espaçador
                if idx > 0:
                    content_layout.addSpacing(5)
                
                crit_title = crit.get("Critério", "")
                # Estilizando o título do critério
                title_label = QLabel(f"Critério: {crit_title}")
                title_label.setStyleSheet("""
                    color: #8AB4F7;  /* Azul suave para contraste */
                    font-weight: bold;
                    font-size: 14px;
                    padding: 5px 10px;
                """)
                title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                title_label.setWordWrap(True)
                title_label.setMaximumWidth(content_widget.width() - 10 if content_widget.width() > 0 else 300)
                        
                # Estilizando o TableWidget
                table_widget = QTableWidget()
                table_widget.setColumnCount(2)
                table_widget.setHorizontalHeaderLabels(["Descrição", "Pts"])

                table_widget.setItemDelegateForColumn(1, EditablePtsDelegate(table_widget, category, crit_title, load_model_from_config))

                table_widget.setStyleSheet("""
                    QTableWidget {
                        background-color: #181928;  /* Fundo escuro */
                        color: white;  /* Texto claro */
                        gridline-color: #25283D;  /* Linhas separadoras discretas */
                        selection-background-color: #2A2D44;  /* Destaque ao selecionar */
                        selection-color: white;
                        border: 1px solid #25283D;
                        alternate-background-color: #1F2133;  /* Linhas alternadas */
                                           font-size: 16px;
                    }

                    QHeaderView::section {
                        background-color: #25283D;  /* Cabeçalhos com fundo escuro */
                        color: white;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 2px;
                        border: 1px solid #2F324B;
                    }

                    QTableCornerButton::section {
                        background-color: #25283D;
                        border: 1px solid #2F324B;
                    }
                """)

                
                # Centraliza os cabeçalhos da tabela
                for col in range(table_widget.columnCount()):
                    header_item = table_widget.horizontalHeaderItem(col)
                    if header_item:
                        header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                options = crit.get("opcoes", [])
                table_widget.setRowCount(len(options))
                for row_idx, option in enumerate(options):
                    desc = str(option.get("Descrição", ""))
                    pont = str(option.get("Pontuação", ""))
                    desc_item = QTableWidgetItem(desc)
                    desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)


                    pont_item = QTableWidgetItem(pont)
                    
                    # Centraliza o conteúdo nas células
                    desc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    pont_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    table_widget.setItem(row_idx, 0, desc_item)
                    table_widget.setItem(row_idx, 1, pont_item)

                # Configura o redimensionamento das colunas
                table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
                table_widget.horizontalHeader().resizeSection(1, 100)  # Define largura fixa de 100 para coluna Pontuação
                table_widget.verticalHeader().setVisible(False)
                
                # Permitir quebra de linha nas células
                table_widget.setWordWrap(True)
                
                # Desativa scrollbars internas e ajusta o tamanho para mostrar tudo
                table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                adjust_table_size(table_widget)

                content_layout.addWidget(title_label)
                content_layout.addWidget(table_widget, 0, Qt.AlignmentFlag.AlignTop)  # Alinhar a tabela ao topo
            # Adicionar um espaçador expansível no final para empurrar todo o conteúdo para cima
            content_layout.addStretch(1)

            # Configurar o scroll para iniciar no topo
            scroll_area.setWidget(content_widget)
            scroll_area.ensureVisible(0, 0)
            scroll_area.verticalScrollBar().setValue(0)
            
            # Desativar o foco no scroll area para evitar problemas de rolagem
            scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            
            group_layout.addWidget(scroll_area)

            criteria_layout.addWidget(group_box)

        criteria_layout.update()

    update_criteria_groupboxes()
    main_layout.addWidget(criteria_container)

    def export_to_excel():
        from datetime import datetime
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices

        datahora = datetime.now().strftime("%d%m%Y_%H%M")
        default_filename = f"mapa_criterio_{datahora}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            main_frame,
            "Exportar para Excel",
            default_filename,
            "Arquivos Excel (*.xlsx)"
        )
        if not file_path:
            return

        config = load_config()
        if not config:
            QMessageBox.critical(main_frame, "Erro", "Configuração não encontrada.")
            return

        try:
            # Preparar dados da aba Compilado
            multiplicadores = config.get("multiplicador", {"materialidade": 4, "relevancia": 2, "criticidade": 4})
            objetos = config.get("objetos_auditaveis", [])
            compilado_data = []
            for obj in objetos:
                nr = obj.get("nr", "")
                descricao = obj.get("descricao", "")
                mat_raw = sum(v.get("valor", 0) for v in obj.get("materialidade", {}).values())
                rel_raw = sum(v.get("valor", 0) for v in obj.get("relevancia", {}).values())
                crit_raw = sum(v.get("valor", 0) for v in obj.get("criticidade", {}).values())
                mat_val = mat_raw * multiplicadores.get("materialidade", 4)
                rel_val = rel_raw * multiplicadores.get("relevancia", 2)
                crit_val = crit_raw * multiplicadores.get("criticidade", 4)
                total = mat_val + rel_val + crit_val

                risco = obj.get("risco", "")
                if not risco:
                    riscos = config.get("riscos", {"Muito Alto": 250, "Alto": 200, "Médio": 150, "Baixo": 100, "Muito Baixo": 50})
                    sorted_riscos = sorted(riscos.items(), key=lambda x: x[1], reverse=True)
                    for label, threshold in sorted_riscos:
                        if total >= threshold:
                            risco = label
                            break
                    else:
                        risco = sorted_riscos[-1][0]

                compilado_data.append({
                    "NR": nr,
                    "Objetos Auditáveis": descricao,
                    "Materialidade": mat_val,
                    "Relevância": rel_val,
                    "Criticidade": crit_val,
                    "Total": total,
                    "Risco": risco
                })
            df_compilado = pd.DataFrame(compilado_data)

            # Função auxiliar para construir DataFrame das abas de critérios
            def build_df(chave):
                dados = []
                for criterio in config.get("pontuacao_criterios", {}).get(chave, []):
                    for opcao in criterio.get("opcoes", []):
                        dados.append({
                            "Critério": criterio.get("Critério", ""),
                            "Tipo": criterio.get("Tipo", ""),
                            "Descrição": opcao.get("Descrição", ""),
                            "Pontuação": opcao.get("Pontuação", "")
                        })
                return pd.DataFrame(dados)

            df_materialidade = build_df("materialidade")
            df_relevancia = build_df("relevancia")
            df_criticidade = build_df("criticidade")

            # Gravação em arquivo Excel
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                df_compilado.to_excel(writer, sheet_name="Compilado", index=False)
                df_materialidade.to_excel(writer, sheet_name="Materialidade", index=False)
                df_relevancia.to_excel(writer, sheet_name="Relevância", index=False)
                df_criticidade.to_excel(writer, sheet_name="Criticidade", index=False)

            QMessageBox.information(main_frame, "Sucesso", "Exportação realizada com sucesso!")
            # Abre automaticamente o arquivo gerado
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(main_frame, "Erro", f"Falha ao exportar para Excel: {e}")

    def import_from_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            main_frame,
            "Importar do Excel",
            "",
            "Arquivos Excel (*.xlsx)"
        )
        if file_path:
            excel_manager = ExcelModelManager(file_path)
            if excel_manager.validate():
                df_compilado = pd.read_excel(file_path, sheet_name="Compilado", dtype=str).fillna("")
                df_materialidade = pd.read_excel(file_path, sheet_name="Materialidade")
                df_relevancia = pd.read_excel(file_path, sheet_name="Relevância")
                df_criticidade = pd.read_excel(file_path, sheet_name="Criticidade")

                objetos_auditaveis = []
                mat_criterios = df_materialidade["Critério"].dropna().unique().tolist()
                rel_criterios = df_relevancia["Critério"].dropna().unique().tolist()
                crit_criterios = df_criticidade["Critério"].dropna().unique().tolist()

                # Criar dicionários para mapear critérios e suas opções
                def create_options_dict(df):
                    options_dict = {}
                    for _, row in df.iterrows():
                        criterio = row["Critério"]
                        if criterio not in options_dict:
                            options_dict[criterio] = {}
                        options_dict[criterio][row["Pontuação"]] = row["Descrição"]
                    return options_dict

                mat_options = create_options_dict(df_materialidade)
                rel_options = create_options_dict(df_relevancia)
                crit_options = create_options_dict(df_criticidade)

                # Inicializar dicionários com valor 0 e texto padrão
                materialidade_dict = {crit: {"valor": 0, "texto": mat_options[crit][0] if 0 in mat_options[crit] else ""} for crit in mat_criterios}
                relevancia_dict = {crit: {"valor": 0, "texto": rel_options[crit][0] if 0 in rel_options[crit] else ""} for crit in rel_criterios}
                criticidade_dict = {crit: {"valor": 0, "texto": crit_options[crit][0] if 0 in crit_options[crit] else ""} for crit in crit_criterios}

                for _, row in df_compilado.iterrows():
                    nr = row["NR"]
                    descricao = row["Objetos Auditáveis"]
                    detalhamento = row["Detalhamento"] if "Detalhamento" in df_compilado.columns else ""
                    objetos_auditaveis.append({
                        "nr": nr,
                        "descricao": descricao,
                        "detalhamento": detalhamento,
                        "materialidade": materialidade_dict.copy(),
                        "relevancia": relevancia_dict.copy(),
                        "criticidade": criticidade_dict.copy()
                    })

                def build_pontuacao(df):
                    agrupado = df.groupby("Critério")
                    itens = []
                    for criterio, grupo in agrupado:
                        tipo = grupo["Tipo"].iloc[0]
                        opcoes = []
                        for _, r in grupo.iterrows():
                            opcoes.append({
                                "Descrição": r["Descrição"],
                                "Pontuação": r["Pontuação"]
                            })
                        itens.append({
                            "Critério": criterio,
                            "Tipo": tipo,
                            "opcoes": opcoes
                        })
                    return itens

                pontuacao_criterios = {
                    "relevancia": build_pontuacao(df_relevancia),
                    "materialidade": build_pontuacao(df_materialidade),
                    "criticidade": build_pontuacao(df_criticidade)
                }

                # Cria o item pai "riscos" com os 5 níveis e seus thresholds
                config = {
                    "objetos_auditaveis": objetos_auditaveis,
                    "multiplicador": {"materialidade": 4, "relevancia": 2, "criticidade": 4},
                    "pontuacao_criterios": pontuacao_criterios,
                    "riscos": {"Muito Alto": 250, "Alto": 200, "Médio": 150, "Baixo": 100, "Muito Baixo": 50}
                }

                try:
                    with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    QMessageBox.information(main_frame, "Sucesso", "Configuração salva com sucesso!")
                    load_model_from_config()
                    update_criteria_groupboxes()
                    load_model_from_config()  # Recarrega o TableView
                except Exception as e:
                    QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar a configuração: {e}")

    def on_table_double_clicked(index):
        """Função chamada quando o usuário clica duas vezes em uma linha da tabela"""
        if not index.isValid():
            return
        
        row = index.row()
        
        # Carregar a configuração atual
        config = load_config()
        if not config:
            QMessageBox.critical(main_frame, "Erro", "Não foi possível carregar a configuração.")
            return
        
        # Obter o objeto auditável correspondente à linha clicada
        objetos_auditaveis = config.get("objetos_auditaveis", [])
        if row >= len(objetos_auditaveis):
            QMessageBox.critical(main_frame, "Erro", "Índice de linha inválido.")
            return
        
        objeto_auditavel = objetos_auditaveis[row]
        
        # Criar e exibir o diálogo de edição
        dialog = EditDialog(main_frame, objeto_auditavel, config, row)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Atualizar o objeto auditável com os dados do diálogo
            updated_objeto = dialog.get_updated_data()
            
            # Obter os multiplicadores
            multiplicadores = config.get("multiplicador", {
                "materialidade": 4,
                "relevancia": 2,
                "criticidade": 4
            })
            
            # Calcular os novos valores
            mat_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
                             for v in updated_objeto.get("materialidade", {}).values())
            rel_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
                             for v in updated_objeto.get("relevancia", {}).values())
            crit_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
                              for v in updated_objeto.get("criticidade", {}).values())
            
            # Aplicar multiplicadores
            mat_val = mat_val_raw * multiplicadores.get("materialidade", 4)
            rel_val = rel_val_raw * multiplicadores.get("relevancia", 2)
            crit_val = crit_val_raw * multiplicadores.get("criticidade", 4)
            
            # Calcular o total
            total = mat_val + rel_val + crit_val
            
            # Atualizar o objeto com os novos valores calculados
            updated_objeto["total"] = total
            
            # Atualizar o objeto na lista
            objetos_auditaveis[row] = updated_objeto
            
            # Atualizar o arquivo JSON
            config["objetos_auditaveis"] = objetos_auditaveis
            try:
                with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                # Recarregar a tabela para refletir as alterações
                load_model_from_config()
                QMessageBox.information(main_frame, "Sucesso", "Dados atualizados com sucesso!")
            except Exception as e:
                QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar no JSON: {e}")
    
    # Conectar o evento de duplo clique na tabela
    table_view.doubleClicked.connect(on_table_double_clicked)

    btn_import.clicked.connect(import_from_excel)
    btn_export.clicked.connect(export_to_excel)
    btn_riscos.clicked.connect(lambda: print("Riscos"))
    btn_multiplicadores.clicked.connect(lambda: print("Multiplicadores"))

    return main_frame

class CustomDoubleSpinBox(QDoubleSpinBox):
    def textFromValue(self, value: float) -> str:
        # Exibe sem casas decimais se não houver dígitos significativos após o separador
        if value == int(value):
            return str(int(value))
        return super().textFromValue(value)

    def valueFromText(self, text: str) -> float:
        # Remove espaços, substitui vírgula por ponto e, se iniciar com separador, adiciona '0'
        text = text.strip().replace(',', '.')
        if text.startswith('.'):
            text = '0' + text
        try:
            return float(text)
        except ValueError:
            return 0.0

class EditablePtsDelegate(QStyledItemDelegate):
    def __init__(self, table_widget, category: str, crit_title: str, update_callback, *args, **kwargs):
        super().__init__(table_widget, *args, **kwargs)
        self.category = category
        self.crit_title = crit_title
        self.update_callback = update_callback

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            editor = CustomDoubleSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(1000)  # ajuste conforme necessário
            editor.setDecimals(2)    # permite valores com casas decimais
            editor.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            editor.setStyleSheet("color: white; background-color: #181928;")
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        try:
            value = float(value)
        except Exception:
            value = 0.0
        # Armazena o valor original para o caso de o usuário não alterar o valor
        editor._initial_value = value
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        if editor.lineEdit().text().strip() == "":
            new_value = editor._initial_value
        else:
            new_value = editor.value()
        # Converte para inteiro apenas se não houver casas decimais significativas
        if new_value == int(new_value):
            new_value = int(new_value)
        model.setData(index, new_value, Qt.ItemDataRole.EditRole)
        option_index = index.row()
        update_json_config(self.category, self.crit_title, option_index, new_value)
        if self.update_callback:
            self.update_callback()


def update_json_config(category: str, crit_title: str, option_index: int, new_value: int):
    try:
        with open(CONFIG_PAINT_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print("Erro ao carregar JSON:", e)
        return

    # Atualiza pontuacao_criterios e captura a descrição da opção alterada.
    criterios = config.get("pontuacao_criterios", {}).get(category, [])
    target_desc = None
    for criterio in criterios:
        if criterio.get("Critério") == crit_title:
            opcoes = criterio.get("opcoes", [])
            if 0 <= option_index < len(opcoes):
                target_desc = opcoes[option_index].get("Descrição")
                opcoes[option_index]["Pontuação"] = new_value
            break

    if target_desc is None:
        print("Critério ou opção não encontrada.")
        return

    # Atualiza os objetos_auditaveis somente para os itens cujo "texto" seja compatível
    for obj in config.get("objetos_auditaveis", []):
        if category in obj and crit_title in obj[category]:
            if obj[category][crit_title].get("texto") == target_desc:
                obj[category][crit_title]["valor"] = new_value

    try:
        with open(CONFIG_PAINT_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("JSON atualizado com sucesso.")
    except Exception as e:
        print("Erro ao salvar JSON:", e)

