from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import pandas as pd
import chardet
import webbrowser
from .dashboard.dash_popup import DashboardPopup

class CartaoCorporativoController(QObject): 
    def __init__(self, icons, view, model):
        super().__init__()
        self.icons = icons
        self.view = view
        self.model = model  # 🔹 Agora estamos passando diretamente o QSqlTableModel

        self.setup_connections()

    def setup_connections(self):
        """Conecta os sinais da View ao Controller"""
        self.view.refreshRequested.connect(self.import_xlsx_to_db)
        self.view.rowDoubleClicked.connect(self.row_double_clicked)
        self.view.linkDataCartaoPagamentoGov.connect(self.open_link)  # 🔹 Conecta o botão ao método
        self.view.open_dashboard.connect(self.open_dashboard)  # 🔹 Conecta o botão ao métod
        
    def open_dashboard(self):
        """Abre o popup do dashboard com os dados do model."""
        data = self.model.get_all_model_data()

        if not data:
            QMessageBox.warning(self.view, "Aviso", "Nenhum dado disponível para exibir no Dashboard.")
            return

        # 🔹 Converter para DataFrame caso `data` seja uma lista de dicionários
        df_unique_orgaos = pd.DataFrame(data)[["cod_orgao", "nome_orgao"]].drop_duplicates()

        self.dashboard_popup = DashboardPopup(df_unique_orgaos, self.model.get_data_for_orgao)

        self.dashboard_popup.exec()

    def open_link(self):
        """Abre o link do Portal da Transparência no navegador."""
        url = "https://portaldatransparencia.gov.br/download-de-dados/cpgf"
        webbrowser.open(url)  # 🔹 Abre o link no navegador padrão
    
    def import_xlsx_to_db(self):
        """Abre um arquivo XLSX ou CSV e importa os dados para o banco de dados."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self.view, 
            "Selecionar Arquivo XLSX ou CSV", 
            "", 
            "Arquivos Suportados (*.xlsx *.csv);;Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if not file_path:
            return  # Se o usuário cancelar, não faz nada.

        try:
            # 🔹 **Detecta o formato do arquivo**
            if file_path.endswith(".csv"):
                # 🔹 **Detecta automaticamente a codificação do arquivo**
                with open(file_path, "rb") as f:
                    result = chardet.detect(f.read(100000))  # Lê os primeiros 100kB para detectar a codificação
                
                encoding_detected = result["encoding"] if result["encoding"] else "utf-8"
                
                # 🔹 **Lê o CSV com a codificação detectada**
                df = pd.read_csv(
                    file_path, 
                    dtype=str, 
                    sep=None,  # Detecta automaticamente o separador
                    engine="python", 
                    encoding=encoding_detected
                )
            else:  # XLSX
                df = pd.read_excel(file_path, dtype=str)

            # 🔹 **Mapeamento de colunas do arquivo para o banco**
            column_mapping = {
                "CÓDIGO ÓRGÃO SUPERIOR": "cod_orgao_superior",
                "NOME ÓRGÃO SUPERIOR": "nome_orgao_superior",
                "CÓDIGO ÓRGÃO": "cod_orgao",
                "NOME ÓRGÃO": "nome_orgao",
                "CÓDIGO UNIDADE GESTORA": "cod_unidade_gestora",
                "NOME UNIDADE GESTORA": "nome_unidade_gestora",
                "ANO EXTRATO": "ano_extrato",
                "MÊS EXTRATO": "mes_extrato",
                "CPF PORTADOR": "cpf_portador",
                "NOME PORTADOR": "nome_portador",
                "CNPJ OU CPF FAVORECIDO": "cnpj_cpf_favorecido",
                "NOME FAVORECIDO": "nome_favorecido",
                "TRANSAÇÃO": "transacao",
                "DATA TRANSAÇÃO": "data_transacao",
                "VALOR TRANSAÇÃO": "valor_transacao",
            }

            df.rename(columns=column_mapping, inplace=True)

            # 🔹 **Corrige valores monetários e converte para float**
            if "valor_transacao" in df.columns:
                df["valor_transacao"] = (
                    df["valor_transacao"]
                    .str.replace(",", ".", regex=True)  # Troca vírgula por ponto
                    .str.replace("[^0-9.]", "", regex=True)  # Remove caracteres não numéricos
                    .astype(float)  # Converte para float
                )

            # 🔹 **Insere os dados no banco de dados**
            with self.model.database_manager as conn:
                df.to_sql("tabela_cartao_corporativo", conn, if_exists="append", index=False)

            QMessageBox.information(self.view, "Sucesso", "Dados importados com sucesso!")

            # 🔹 **Agora chama a atualização da tabela**
            self.view.model.select()

        except Exception as e:
            QMessageBox.warning(self.view, "Erro", f"Falha ao importar o arquivo: {e}")
            
    def row_double_clicked(self, row_data):
        """Handles row double-click event."""
        pass

