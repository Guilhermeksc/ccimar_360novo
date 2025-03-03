import os
import json
import pandas as pd
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QStyledItemDelegate,
    QGroupBox, QTableWidget, QTableWidgetItem, QScrollArea, QWidget,
    QSizePolicy, QDialog, QComboBox, QFormLayout, QTabWidget, QDialogButtonBox,
    QSpinBox, QLineEdit
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt
from paths import OM_REPRESENTATIVAS_PATH
from .tableview import CustomTableView, ExcelModelManager, load_config
from .calculations import MultiplicadoresDialog
from .percentual import PercentualDialog

def create_om_representativas(title_text):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Barra de título e botões
    title_layout = QHBoxLayout()
    title_label = QLabel("Mapa de Critérios e Pesos - OM Representativas")
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()

    # Estilo uniforme para os botões no tema escuro
    button_style = """
        QPushButton {
            background-color: #25283D;  /* Fundo escuro sutil */
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid #3A3D56;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #303456;  /* Cor levemente mais clara ao passar o mouse */
            border: 1px solid #4A4F78;
        }

        QPushButton:pressed {
            background-color: #1E2035;
            border: 1px solid #6B6F9A;
        }
    """

    btn_export = QPushButton("Exportar")
    btn_export.setStyleSheet(button_style)
    title_layout.addWidget(btn_export)

    btn_import = QPushButton("Importar")
    btn_import.setStyleSheet(button_style)
    title_layout.addWidget(btn_import)

    def open_percentual_dialog():
        dialog = PercentualDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            load_model_from_config()  # Recarrega a tabela após salvar

    btn_percentual = QPushButton("Percentual")
    btn_percentual.setStyleSheet(button_style)
    title_layout.addWidget(btn_percentual)
    btn_percentual.clicked.connect(open_percentual_dialog)

    def open_multiplicadores_dialog():
        dialog = MultiplicadoresDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            load_model_from_config()  # Recarrega a tabela após salvar

    btn_multiplicadores = QPushButton("Multiplicadores")
    btn_multiplicadores.setStyleSheet(button_style)
    title_layout.addWidget(btn_multiplicadores)
    btn_multiplicadores.clicked.connect(open_multiplicadores_dialog)

    # Botão de full screen para o mapa (table_view)
    btn_fullscreen = QPushButton("Mapa Full Screen")
    btn_fullscreen.setStyleSheet(button_style)
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
   
    main_layout.addLayout(title_layout)

    # Tabela principal (CustomTableView)
    table_view = CustomTableView()
    table_view.setFont(QFont("Arial", 12))  # Define fonte maior para melhor visibilidade

    table_view.setStyleSheet("""
        QTableView {
            background-color: #181928;  /* Fundo da tabela */
            color: white;  /* Cor do texto */
            gridline-color: #25283D;  /* Linhas separadoras discretas */
            selection-background-color: #2A2D44;  /* Fundo ao selecionar */
            selection-color: white;
            border: 1px solid #25283D;
            alternate-background-color: #1F2133; /* Linhas alternadas */
        }
        
        QHeaderView::section {
            background-color: #25283D;  /* Cabeçalhos escuros */
            color: white;
            padding: 6px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #2F324B;
        }

        QTableCornerButton::section {
            background-color: #25283D;
            border: 1px solid #2F324B;
        }
    """)

    model = QStandardItemModel()
    table_view.setModel(model)
    headers = ["Critério", "Descrição", "Percentual", "Parâmetro", "Pontos", "Peso"]
    model.setHorizontalHeaderLabels(headers)
    
    # Centraliza os cabeçalhos da tabela principal
    for col in range(len(headers)):
        header_item = model.horizontalHeaderItem(col)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    table_view.verticalHeader().setDefaultSectionSize(30)
    main_layout.addWidget(table_view)

    def load_model_from_config():
        config = load_config()
        model.clear()

        if not config:
            return

        headers = ["Critério", "Descrição", "Percentual", "Parâmetro", "Pontos", "Peso"]
        model.setHorizontalHeaderLabels(headers)

        for parent in config.get("mapa_om_representativas", []):
            criterio = parent.get("Critério", "")
            peso = parent.get("Peso", "")
            for child in parent.get("itens", []):
                # Formatação do valor percentual:
                percentual = child.get("Percentual", 0.0)
                try:
                    percentual_num = float(percentual)
                except (ValueError, TypeError):
                    percentual_num = 0.0

                if percentual_num == 0.0:
                    percentual_text = "-"
                else:
                    percentual_text = f"{int(percentual_num * 100)}%"

                descricao = child.get("Descrição", "")
                parametro = child.get("Parâmetro", "")
                pontos = child.get("Pontos", "")
                row = [
                    QStandardItem(str(criterio)),
                    QStandardItem(str(descricao)),
                    QStandardItem(percentual_text),
                    QStandardItem(str(parametro)),
                    QStandardItem(str(pontos)),
                    QStandardItem(str(peso)),
                ]
                for cell in row:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                model.appendRow(row)

        table_view.setColumnWidth(0, 130)
        table_view.setColumnWidth(2, 100)
        table_view.setColumnWidth(3, 100)
        table_view.setColumnWidth(4, 65)
        table_view.setColumnWidth(5, 60)
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
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("Arquivo JSON atualizado com sucesso.")
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Falha ao salvar no JSON: {e}")

        # Atualiza o modelo do table_view com os novos valores
        load_model_from_config()

    # Conectar evento de alteração dos dados na tabela
    model.dataChanged.connect(update_json_from_table)

    def import_from_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            main_frame,
            "Importar do Excel",
            "",
            "Arquivos Excel (*.xlsx)"
        )
        if not file_path:
            return

        excel_manager = ExcelModelManager(file_path)
        if not excel_manager.validate():
            return

        try:
            df = pd.read_excel(file_path, sheet_name="Mapa OM Representativas")
        except Exception as e:
            QMessageBox.critical(main_frame, "Erro", f"Erro ao ler a aba 'Mapa OM Representativas': {e}")
            return

        # Garante que a coluna "Parâmetro" mantenha "N/A" como texto
        if "Parâmetro" in df.columns:
            df["Parâmetro"] = df["Parâmetro"].fillna("N/A")

        # Agrupa os dados pelo campo "Critério"
        grouped_data = []
        for criterio, group in df.groupby("Critério"):
            parent_item = {
                "Critério": criterio,
                "Peso": int(group["Peso"].max()),
                "itens": []
            }
            for _, row in group.iterrows():
                child_item = {
                    "Descrição": row["Descrição"],
                    "Percentual": row["Percentual"],
                    "Parâmetro": row["Parâmetro"],
                    "Pontos": row["Pontos"]
                }
                parent_item["itens"].append(child_item)
            grouped_data.append(parent_item)

        config = {"mapa_om_representativas": grouped_data}

        try:
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(main_frame, "Sucesso", "Configuração salva com sucesso!")
            load_model_from_config()
        except Exception as e:
            QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar a configuração: {e}")

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
        if not config or "mapa_om_representativas" not in config:
            QMessageBox.critical(main_frame, "Erro", "Configuração inválida ou vazia.")
            return

        # Constrói as linhas para o DataFrame
        rows = []
        for parent in config["mapa_om_representativas"]:
            criterio = parent.get("Critério", "")
            peso = parent.get("Peso", "")
            for child in parent.get("itens", []):
                row = {
                    "Critério": criterio,
                    "Descrição": child.get("Descrição", ""),
                    "Percentual": child.get("Percentual", 0.0),
                    "Parâmetro": child.get("Parâmetro", ""),
                    "Pontos": child.get("Pontos", ""),
                    "Peso": peso
                }
                rows.append(row)

        df = pd.DataFrame(rows, columns=["Critério", "Descrição", "Percentual", "Parâmetro", "Pontos", "Peso"])
        try:
            df.to_excel(file_path, index=False)
            QMessageBox.information(main_frame, "Sucesso", f"Dados exportados com sucesso para:\n{file_path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(main_frame, "Erro", f"Falha ao exportar para Excel: {e}")



    # def on_table_double_clicked(index):
    #     """Função chamada quando o usuário clica duas vezes em uma linha da tabela"""
    #     if not index.isValid():
    #         return
        
    #     row = index.row()
        
    #     # Carregar a configuração atual
    #     config = load_config()
    #     if not config:
    #         QMessageBox.critical(main_frame, "Erro", "Não foi possível carregar a configuração.")
    #         return
        
    #     # Obter o objeto auditável correspondente à linha clicada
    #     objetos_auditaveis = config.get("objetos_auditaveis", [])
    #     if row >= len(objetos_auditaveis):
    #         QMessageBox.critical(main_frame, "Erro", "Índice de linha inválido.")
    #         return
        
    #     objeto_auditavel = objetos_auditaveis[row]
        
    #     # Criar e exibir o diálogo de edição
    #     dialog = EditDialog(main_frame, objeto_auditavel, config, row)
    #     if dialog.exec() == QDialog.DialogCode.Accepted:
    #         # Atualizar o objeto auditável com os dados do diálogo
    #         updated_objeto = dialog.get_updated_data()
            
    #         # Obter os multiplicadores
    #         multiplicadores = config.get("multiplicador", {
    #             "materialidade": 4,
    #             "relevancia": 2,
    #             "criticidade": 4
    #         })
            
    #         # Calcular os novos valores
    #         mat_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
    #                          for v in updated_objeto.get("materialidade", {}).values())
    #         rel_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
    #                          for v in updated_objeto.get("relevancia", {}).values())
    #         crit_val_raw = sum(v.get("valor", 0) if isinstance(v, dict) else 0 
    #                           for v in updated_objeto.get("criticidade", {}).values())
            
    #         # Aplicar multiplicadores
    #         mat_val = mat_val_raw * multiplicadores.get("materialidade", 4)
    #         rel_val = rel_val_raw * multiplicadores.get("relevancia", 2)
    #         crit_val = crit_val_raw * multiplicadores.get("criticidade", 4)
            
    #         # Calcular o total
    #         total = mat_val + rel_val + crit_val
            
    #         # Atualizar o objeto com os novos valores calculados
    #         updated_objeto["total"] = total
            
    #         # Atualizar o objeto na lista
    #         objetos_auditaveis[row] = updated_objeto
            
    #         # Atualizar o arquivo JSON
    #         config["objetos_auditaveis"] = objetos_auditaveis
    #         try:
    #             with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
    #                 json.dump(config, f, indent=4, ensure_ascii=False)
                
    #             # Recarregar a tabela para refletir as alterações
    #             load_model_from_config()
    #             QMessageBox.information(main_frame, "Sucesso", "Dados atualizados com sucesso!")
    #         except Exception as e:
    #             QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar no JSON: {e}")
    
    # Conectar o evento de duplo clique na tabela
    # table_view.doubleClicked.connect(on_table_double_clicked)

    btn_import.clicked.connect(import_from_excel)
    btn_export.clicked.connect(export_to_excel)
    btn_multiplicadores.clicked.connect(lambda: print("Multiplicadores"))

    return main_frame
