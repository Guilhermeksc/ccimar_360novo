import pandas as pd
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QDialog,
    QFileDialog, QDialog, QProgressBar
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from .tableview import CustomTableView, CSVModelManager, load_config
from .dashboard import DashboardDialog
from utils.styles import apply_table_style, apply_button_style
from database.db_manager import DatabaseManager
from paths import ACOES_ORCAMENTARIAS_SQL_PATH
import chardet
from utils.styles.style_add_button import add_button_func

def create_acoes_orcamentarias(title_text, icons):
    icons = icons
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Barra de título e botões
    title_layout = QHBoxLayout()
    title_label = QLabel("Ações Orçamentárias")
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()
    
    def dashboard():
        db_manager = DatabaseManager(ACOES_ORCAMENTARIAS_SQL_PATH)
        dlg = DashboardDialog(parent=main_frame, db_manager=db_manager)
        dlg.exec()
    
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

    # btn_fullscreen.clicked.connect(open_fullscreen_tableview)
   
    main_layout.addLayout(title_layout)

    # Tabela principal (CustomTableView)
    table_view = CustomTableView()
    table_view.setFont(QFont("Arial", 12))  # Define fonte maior para melhor visibilidade

    apply_table_style(table_view)

    model = QStandardItemModel()
    table_view.setModel(model)
    headers = ["Cod.Un.Orçamentária", "NOME UNIDADE ORÇAMENTÁRIA", "NOME FUNÇÃO", "NOME SUBFUNÇÃO", "NOME PROGRAMA ORÇAMENTÁRIO", "Peso"]
    model.setHorizontalHeaderLabels(headers)
    
    # Centraliza os cabeçalhos da tabela principal
    for col in range(len(headers)):
        header_item = model.horizontalHeaderItem(col)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    table_view.verticalHeader().setDefaultSectionSize(30)
    main_layout.addWidget(table_view)

    def load_model_from_config():
        db_manager = DatabaseManager(ACOES_ORCAMENTARIAS_SQL_PATH)
        table_name = "orcamento_despesa"  # Tabela fixa

        # Verifica se a tabela existe
        exists = db_manager.fetch_all(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not exists:
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                exercicio TEXT,
                codigo_orgao_superior TEXT,
                nome_orgao_superior TEXT,
                codigo_orgao_subordinado TEXT,
                nome_orgao_subordinado TEXT,
                codigo_unidade_orcamentaria TEXT,
                nome_unidade_orcamentaria TEXT,
                codigo_funcao TEXT,
                nome_funcao TEXT,
                codigo_subfuncao TEXT,
                nome_subfuncao TEXT,
                codigo_programa_orcamentario TEXT,
                nome_programa_orcamentario TEXT,
                codigo_acao TEXT,
                nome_acao TEXT,
                codigo_categoria_economica TEXT,
                nome_categoria_economica TEXT,
                codigo_grupo_despesa TEXT,
                nome_grupo_despesa TEXT,
                codigo_elemento_despesa TEXT,
                nome_elemento_despesa TEXT,
                orcamento_inicial REAL,
                orcamento_atualizado REAL,
                orcamento_empenhado REAL,
                orcamento_realizado REAL,
                percentual_realizado REAL
            );
            """
            db_manager.execute_update(create_sql)

        data = db_manager.fetch_all(f'SELECT * FROM "{table_name}"')
        
        model.clear()
        headers = ["EXERCÍCIO", "CÓDIGO ÓRGÃO SUPERIOR", "NOME ÓRGÃO SUPERIOR",
                "CÓDIGO ÓRGÃO SUBORDINADO", "NOME ÓRGÃO SUBORDINADO",
                "CÓDIGO UNIDADE ORÇAMENTÁRIA", "NOME UNIDADE ORÇAMENTÁRIA",
                "CÓDIGO FUNÇÃO", "NOME FUNÇÃO", "CÓDIGO SUBFUNÇÃO", "NOME SUBFUNÇÃO",
                "CÓDIGO PROGRAMA ORÇAMENTÁRIO", "NOME PROGRAMA ORÇAMENTÁRIO",
                "CÓDIGO AÇÃO", "NOME AÇÃO", "CÓDIGO CATEGORIA ECONÔMICA",
                "NOME CATEGORIA ECONÔMICA", "CÓDIGO GRUPO DE DESPESA",
                "NOME GRUPO DE DESPESA", "CÓDIGO ELEMENTO DE DESPESA",
                "NOME ELEMENTO DE DESPESA", "ORÇAMENTO INICIAL (R$)",
                "ORÇAMENTO ATUALIZADO (R$)", "ORÇAMENTO EMPENHADO (R$)",
                "ORÇAMENTO REALIZADO (R$)", "% REALIZADO DO ORÇAMENTO (COM RELAÇÃO AO ORÇAMENTO ATUALIZADO)"]
        model.setHorizontalHeaderLabels(headers)
        
        mapping = {
            "EXERCÍCIO": "exercicio",
            "CÓDIGO ÓRGÃO SUPERIOR": "codigo_orgao_superior",
            "NOME ÓRGÃO SUPERIOR": "nome_orgao_superior",
            "CÓDIGO ÓRGÃO SUBORDINADO": "codigo_orgao_subordinado",
            "NOME ÓRGÃO SUBORDINADO": "nome_orgao_subordinado",
            "CÓDIGO UNIDADE ORÇAMENTÁRIA": "codigo_unidade_orcamentaria",
            "NOME UNIDADE ORÇAMENTÁRIA": "nome_unidade_orcamentaria",
            "CÓDIGO FUNÇÃO": "codigo_funcao",
            "NOME FUNÇÃO": "nome_funcao",
            "CÓDIGO SUBFUNÇÃO": "codigo_subfuncao",
            "NOME SUBFUNÇÃO": "nome_subfuncao",
            "CÓDIGO PROGRAMA ORÇAMENTÁRIO": "codigo_programa_orcamentario",
            "NOME PROGRAMA ORÇAMENTÁRIO": "nome_programa_orcamentario",
            "CÓDIGO AÇÃO": "codigo_acao",
            "NOME AÇÃO": "nome_acao",
            "CÓDIGO CATEGORIA ECONÔMICA": "codigo_categoria_economica",
            "NOME CATEGORIA ECONÔMICA": "nome_categoria_economica",
            "CÓDIGO GRUPO DE DESPESA": "codigo_grupo_despesa",
            "NOME GRUPO DE DESPESA": "nome_grupo_despesa",
            "CÓDIGO ELEMENTO DE DESPESA": "codigo_elemento_despesa",
            "NOME ELEMENTO DE DESPESA": "nome_elemento_despesa",
            "ORÇAMENTO INICIAL (R$)": "orcamento_inicial",
            "ORÇAMENTO ATUALIZADO (R$)": "orcamento_atualizado",
            "ORÇAMENTO EMPENHADO (R$)": "orcamento_empenhado",
            "ORÇAMENTO REALIZADO (R$)": "orcamento_realizado",
            "% REALIZADO DO ORÇAMENTO (COM RELAÇÃO AO ORÇAMENTO ATUALIZADO)": "percentual_realizado"
        }

        for row in data:
            items = []
            for header in headers:
                key = mapping[header]
                value = row.get(key, "")
                item = QStandardItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                items.append(item)
            model.appendRow(items)

        adjust_columns()
    def adjust_columns():
        # Define larguras iniciais para as colunas fixas
        table_view.setColumnWidth(0, 85)
        table_view.setColumnWidth(22, 200)
        table_view.setColumnWidth(23, 200)
        table_view.setColumnWidth(24, 200)

        # Ajusta o modo de redimensionamento
        header = table_view.horizontalHeader()
        for col in range(model.columnCount()):
            if col in (4, 14):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            else:
                # Use Interactive ou ResizeToContents no lugar de Fixed
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

        # Exibe apenas as colunas necessárias
        visible_columns = {0, 4, 14, 22, 23, 24}
        for col in range(model.columnCount()):
            table_view.setColumnHidden(col, col not in visible_columns)
            

    load_model_from_config()

    def import_from_csv():
        file_path, _ = QFileDialog.getOpenFileName(None, "Importar do ZIP", "", "Arquivos ZIP (*.zip)")
        if not file_path:
            return

        progress_dialog = ProgressDialog()
        thread = ImportThread(file_path)

        thread.progress_signal.connect(progress_dialog.update_progress)
        thread.finished_signal.connect(lambda msg: (progress_dialog.accept(), print(msg)))

        thread.start()
        progress_dialog.exec()

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

    btn_export = add_button_func("Exportar", "export", export_to_excel, title_layout, icons, tooltip="Exportar dados")
    btn_import = add_button_func("Importar", "zip", import_from_csv, title_layout, icons, tooltip="Importar dados")
    btn_adicionar = add_button_func("Gráficos", "graficos", dashboard, title_layout, icons, tooltip="Adicionar novo item")
    btn_relatorio = add_button_func("Full Screen", "report", open_fullscreen_tableview, title_layout, icons, tooltip="Visualizar relatório")

    btn_import.clicked.connect(import_from_csv)
    btn_export.clicked.connect(export_to_excel)

    return main_frame

db_columns = [
    "exercicio",
    "codigo_orgao_superior",
    "nome_orgao_superior",
    "codigo_orgao_subordinado",
    "nome_orgao_subordinado",
    "codigo_unidade_orcamentaria",
    "nome_unidade_orcamentaria",
    "codigo_funcao",
    "nome_funcao",
    "codigo_subfuncao",
    "nome_subfuncao",
    "codigo_programa_orcamentario",
    "nome_programa_orcamentario",
    "codigo_acao",
    "nome_acao",
    "codigo_categoria_economica",
    "nome_categoria_economica",
    "codigo_grupo_despesa",
    "nome_grupo_despesa",
    "codigo_elemento_despesa",
    "nome_elemento_despesa",
    "orcamento_inicial",
    "orcamento_atualizado",
    "orcamento_empenhado",
    "orcamento_realizado",
    "percentual_realizado"
]

class ImportThread(QThread):
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def detect_encoding_for_bytes(self, data: bytes) -> str:
        """Detecta encoding de um arquivo em bytes usando chardet."""
        result = chardet.detect(data)
        return result['encoding']

    def run(self):
        try:
            import zipfile
            from io import BytesIO

            # Abre o ZIP
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                # Localiza o primeiro CSV no ZIP
                csv_files = [name for name in zf.namelist() if name.lower().endswith('.csv')]
                if not csv_files:
                    raise ValueError("Nenhum arquivo CSV encontrado dentro do .zip.")

                # Lê todo o conteúdo do primeiro CSV em memória
                csv_data = zf.read(csv_files[0])

            # Detecta encoding em memória
            encoding = self.detect_encoding_for_bytes(csv_data)

            # Converte para BytesIO e lê com pandas
            csv_buffer = BytesIO(csv_data)
            df = pd.read_csv(csv_buffer, sep=';', encoding=encoding, decimal=',')

            print("Colunas do CSV carregado:", df.columns.tolist())

            # Filtra os códigos desejados
            codigos_permitidos = {"52233", "52131", "52132"}
            df = df[df["CÓDIGO ÓRGÃO SUBORDINADO"].astype(str).isin(codigos_permitidos)]

            # Mapeamento completo
            column_mapping = {
                "EXERCÍCIO": "exercicio",
                "CÓDIGO ÓRGÃO SUPERIOR": "codigo_orgao_superior",
                "NOME ÓRGÃO SUPERIOR": "nome_orgao_superior",
                "CÓDIGO ÓRGÃO SUBORDINADO": "codigo_orgao_subordinado",
                "NOME ÓRGÃO SUBORDINADO": "nome_orgao_subordinado",
                "CÓDIGO UNIDADE ORÇAMENTÁRIA": "codigo_unidade_orcamentaria",
                "NOME UNIDADE ORÇAMENTÁRIA": "nome_unidade_orcamentaria",
                "CÓDIGO FUNÇÃO": "codigo_funcao",
                "NOME FUNÇÃO": "nome_funcao",
                "CÓDIGO SUBFUNÇÃO": "codigo_subfuncao",
                "NOME SUBFUNÇÃO": "nome_subfuncao",
                "CÓDIGO PROGRAMA ORÇAMENTÁRIO": "codigo_programa_orcamentario",
                "NOME PROGRAMA ORÇAMENTÁRIO": "nome_programa_orcamentario",
                "CÓDIGO AÇÃO": "codigo_acao",
                "NOME AÇÃO": "nome_acao",
                "CÓDIGO CATEGORIA ECONÔMICA": "codigo_categoria_economica",
                "NOME CATEGORIA ECONÔMICA": "nome_categoria_economica",
                "CÓDIGO GRUPO DE DESPESA": "codigo_grupo_despesa",
                "NOME GRUPO DE DESPESA": "nome_grupo_despesa",
                "CÓDIGO ELEMENTO DE DESPESA": "codigo_elemento_despesa",
                "NOME ELEMENTO DE DESPESA": "nome_elemento_despesa",
                "ORÇAMENTO INICIAL (R$)": "orcamento_inicial",
                "ORÇAMENTO ATUALIZADO (R$)": "orcamento_atualizado",
                "ORÇAMENTO EMPENHADO (R$)": "orcamento_empenhado",
                "ORÇAMENTO REALIZADO (R$)": "orcamento_realizado",
                "% REALIZADO DO ORÇAMENTO (COM RELAÇÃO AO ORÇAMENTO ATUALIZADO)": "percentual_realizado"
            }

            # Renomeia colunas no DataFrame
            df.rename(columns=column_mapping, inplace=True)

            # Verifica se todas as colunas mapeadas estão presentes
            missing_cols = [col for col in column_mapping.values() if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Colunas ausentes no CSV após renomeação: {missing_cols}")

            # Converte colunas numéricas
            numeric_cols = ["orcamento_inicial", "orcamento_atualizado", "orcamento_empenhado", "orcamento_realizado", "percentual_realizado"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            db_manager = DatabaseManager(ACOES_ORCAMENTARIAS_SQL_PATH)
            table_name = "orcamento_despesa"
            inserted = 0
            updated = 0

            for _, row in df.iterrows():
                # Preparando para ver se já existe a linha
                # A PK será exercicio+codigo_orgao_superior+...+nome_elemento_despesa+orcamento_inicial
                key_cols = [
                    "exercicio",
                    "codigo_orgao_superior",
                    "nome_orgao_superior",
                    "codigo_orgao_subordinado",
                    "nome_orgao_subordinado",
                    "codigo_unidade_orcamentaria",
                    "nome_unidade_orcamentaria",
                    "codigo_funcao",
                    "nome_funcao",
                    "codigo_subfuncao",
                    "nome_subfuncao",
                    "codigo_programa_orcamentario",
                    "nome_programa_orcamentario",
                    "codigo_acao",
                    "nome_acao",
                    "codigo_categoria_economica",
                    "nome_categoria_economica",
                    "codigo_grupo_despesa",
                    "nome_grupo_despesa",
                    "codigo_elemento_despesa",
                    "nome_elemento_despesa",
                    "orcamento_inicial"  # adicionado como chave
                ]

                # Monta a tupla de chaves
                key_values = tuple(row[k] for k in key_cols)

                # Monta query de SELECT (listando TODAS as colunas) para exibir valores anteriores
                select_query = f"""
                    SELECT {', '.join(db_columns)}
                    FROM {table_name}
                    WHERE exercicio = ?
                      AND codigo_orgao_superior = ?
                      AND nome_orgao_superior = ?
                      AND codigo_orgao_subordinado = ?
                      AND nome_orgao_subordinado = ?
                      AND codigo_unidade_orcamentaria = ?
                      AND nome_unidade_orcamentaria = ?
                      AND codigo_funcao = ?
                      AND nome_funcao = ?
                      AND codigo_subfuncao = ?
                      AND nome_subfuncao = ?
                      AND codigo_programa_orcamentario = ?
                      AND nome_programa_orcamentario = ?
                      AND codigo_acao = ?
                      AND nome_acao = ?
                      AND codigo_categoria_economica = ?
                      AND nome_categoria_economica = ?
                      AND codigo_grupo_despesa = ?
                      AND nome_grupo_despesa = ?
                      AND codigo_elemento_despesa = ?
                      AND nome_elemento_despesa = ?
                      AND orcamento_inicial = ?
                """

                old_data = db_manager.execute_query(select_query, key_values)

                # Monta dicionário com novos valores
                new_data_dict = {col: row[col] for col in db_columns}

                if old_data:
                    # Converte a primeira linha retornada em dicionário
                    old_data_dict = dict(zip(db_columns, old_data[0]))
                    print("---")
                    print("Valores anteriores:", old_data_dict)
                    print("Valores atualizados:", new_data_dict)

                    # Monta a query de UPDATE (lista todas as colunas do DB)
                    # Precisamos adicionar orcamento_inicial no WHERE final
                    update_set = ", ".join([f"{col} = ?" for col in db_columns if col not in key_cols])
                    update_query = f"""
                        UPDATE {table_name}
                        SET {update_set}
                        WHERE exercicio = ?
                          AND codigo_orgao_superior = ?
                          AND nome_orgao_superior = ?
                          AND codigo_orgao_subordinado = ?
                          AND nome_orgao_subordinado = ?
                          AND codigo_unidade_orcamentaria = ?
                          AND nome_unidade_orcamentaria = ?
                          AND codigo_funcao = ?
                          AND nome_funcao = ?
                          AND codigo_subfuncao = ?
                          AND nome_subfuncao = ?
                          AND codigo_programa_orcamentario = ?
                          AND nome_programa_orcamentario = ?
                          AND codigo_acao = ?
                          AND nome_acao = ?
                          AND codigo_categoria_economica = ?
                          AND nome_categoria_economica = ?
                          AND codigo_grupo_despesa = ?
                          AND nome_grupo_despesa = ?
                          AND codigo_elemento_despesa = ?
                          AND nome_elemento_despesa = ?
                          AND orcamento_inicial = ?
                    """

                    # Parametros de UPDATE: todos os col do DB que nao sao chaves + as chaves
                    update_params = [new_data_dict[col] for col in db_columns if col not in key_cols] + list(key_values)
                    db_manager.execute_update(update_query, tuple(update_params))
                    updated += 1
                else:
                    # Monta query de INSERT
                    insert_cols = ", ".join(db_columns)
                    insert_placeholders = ", ".join(["?"] * len(db_columns))
                    insert_query = f"INSERT INTO {table_name} ({insert_cols}) VALUES ({insert_placeholders})"
                    insert_params = [new_data_dict[col] for col in db_columns]
                    db_manager.execute_update(insert_query, tuple(insert_params))
                    inserted += 1

                self.progress_signal.emit(inserted, updated)

            self.finished_signal.emit(f"Importação concluída. Inseridos: {inserted}, Atualizados: {updated}")
        except Exception as e:
            self.finished_signal.emit(f"Erro ao importar ZIP: {e}")

class ProgressDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Importando Dados")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Registros inseridos: 0 | Atualizados: 0")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, inserted, updated):
        self.label.setText(f"Registros inseridos: {inserted} | Atualizados: {updated}")
        self.progress_bar.setValue(inserted + updated)