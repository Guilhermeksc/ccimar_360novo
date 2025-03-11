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
from .multiplicadores import MultiplicadoresDialog
from .percentual import PercentualDialog
from utils.styles import apply_table_style, apply_button_style

def create_om_representativas(title_text, icons):
    icons = icons
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Barra de título e botões
    title_layout = QHBoxLayout()
    title_label = QLabel("ANEXO 'B' CCIMAR 10-02")
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()

    btn_export = QPushButton("Exportar")
    apply_button_style(btn_export)
    title_layout.addWidget(btn_export)

    btn_import = QPushButton("Importar")
    apply_button_style(btn_import)
    title_layout.addWidget(btn_import)

    def open_percentual_dialog():
        dialog = PercentualDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            load_model_from_config()  # Recarrega a tabela após salvar

    btn_percentual = QPushButton("Percentual")
    apply_button_style(btn_percentual)
    title_layout.addWidget(btn_percentual)
    btn_percentual.clicked.connect(open_percentual_dialog)

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
   
    main_layout.addLayout(title_layout)

    # Tabela principal (CustomTableView)
    table_view = CustomTableView()
    table_view.setFont(QFont("Arial", 12))  # Define fonte maior para melhor visibilidade

    apply_table_style(table_view)

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

    btn_import.clicked.connect(import_from_excel)
    btn_export.clicked.connect(export_to_excel)

    return main_frame
