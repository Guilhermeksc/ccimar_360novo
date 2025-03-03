from database.db_manager import DatabaseManager
from .menu.database.insert_munic import insert_munic
from .menu.database.insert_organizacao_militar import insert_organizacao_militar
from .menu.database.insert_auditoria import insert_auditoria
from .menu.database.insert_execucao_licitacao import insert_execucao_licitacao
from .menu.database.insert_pagamento import insert_pagamento
from .menu.database.insert_patrimonio import insert_patrimonio
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from datetime import datetime

class CCIMAR11Model(QObject):
    def __init__(self, database_path, parent=None):
        super().__init__(parent)
        self.database_manager = DatabaseManager(database_path)
        self.db = None
        self.model = None
        self.init_database()

    def init_database(self):
        """Inicializa a conexão com o banco de dados e ajusta a estrutura das tabelas."""
        if QSqlDatabase.contains("my_conn"):
            QSqlDatabase.removeDatabase("my_conn")
        self.db = QSqlDatabase.addDatabase('QSQLITE', "my_conn")
        self.db.setDatabaseName(str(self.database_manager.db_path))

        if not self.db.open():
            print("Não foi possível abrir a conexão com o banco de dados.")
        else:
            print("Conexão com o banco de dados aberta com sucesso.")
            self.create_tables_if_not_exist()

    def setup_model(self, table_name, editable=False):
        """Configura o modelo SQL para a tabela especificada."""
        # Passa o database_manager para o modelo personalizado
        self.model = CustomSqlTableModel(parent=self, db=self.db, database_manager=self.database_manager, non_editable_columns=[4, 8, 10, 13])
        self.model.setTable(table_name)
        
        if editable:
            self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        
        self.model.select()
        return self.model
    
    def create_tables_if_not_exist(self):
        """Cria as tabelas com cod_siafi como PRIMARY KEY."""
        query = QSqlQuery(self.db)

        tabelas = {
            "organizacoes_militares": """
                CREATE TABLE IF NOT EXISTS organizacoes_militares (
                    cod_siafi INTEGER PRIMARY KEY,
                    sigla_om TEXT NOT NULL,
                    nome_om TEXT NOT NULL,
                    distrito TEXT,
                    uf TEXT
                )
            """,
            "auditorias": """
                CREATE TABLE IF NOT EXISTS auditorias (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_siafi INTEGER NOT NULL,
                    ano_auditoria INTEGER NOT NULL,
                    FOREIGN KEY (cod_siafi) REFERENCES organizacoes_militares(cod_siafi)
                )
            """,
            "criterio_execucao_licitacao": """
                CREATE TABLE IF NOT EXISTS criterio_execucao_licitacao (
                    id_execucao INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_siafi INTEGER NOT NULL,
                    valor_convite REAL,
                    valor_tomada_preco REAL,
                    valor_concorrencia REAL,
                    valor_dispensa REAL,
                    valor_inexigibilidade REAL,
                    valor_nao_se_aplica REAL,
                    valor_suprimento_fundos REAL,
                    valor_regime_diferenciado REAL,
                    valor_cons REAL,
                    valor_pregao_eletronico REAL,
                    valor_credenciamento REAL,
                    valor_total_execucao_licitacao REAL,
                    FOREIGN KEY (cod_siafi) REFERENCES organizacoes_militares(cod_siafi)
                )
            """,
            "criterio_pagamento": """
                CREATE TABLE IF NOT EXISTS criterio_pagamento (
                    id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_siafi INTEGER NOT NULL,
                    folha_de_pagamento_total REAL,
                    FOREIGN KEY (cod_siafi) REFERENCES organizacoes_militares(cod_siafi)
                )
            """,
            "criterio_munic": """
                CREATE TABLE IF NOT EXISTS criterio_munic (
                    id_munic INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_siafi INTEGER NOT NULL,
                    codigo_om TEXT NOT NULL,
                    despesa_autorizada REAL,
                    quantidade_de_notas INTEGER,
                    ultima_auditoria TEXT,
                    FOREIGN KEY (cod_siafi) REFERENCES organizacoes_militares(cod_siafi)
                )
            """,
            "criterio_patrimonio": """
                CREATE TABLE IF NOT EXISTS criterio_patrimonio (
                    id_patrimonio INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_siafi INTEGER NOT NULL,
                    total_geral_bens_moveis REAL,
                    importacoes_em_andamento_bens_moveis REAL,
                    total_geral_bens_imoveis REAL,
                    importacoes_em_andamento_bens_imoveis REAL,
                    bens_imoveis_a_classificar REAL,
                    FOREIGN KEY (cod_siafi) REFERENCES organizacoes_militares(cod_siafi)
                )
            """
        }

        for nome_tabela, sql_criacao in tabelas.items():
            if not query.exec(sql_criacao):
                print(f"Erro ao criar/verificar a tabela '{nome_tabela}':", query.lastError().text())
            else:
                print(f"Tabela '{nome_tabela}' criada/verificada com sucesso.")

    def insert_munic(self, df):
        insert_munic(self.database_manager, df)

    def insert_organizacao_militar(self, df):
        insert_organizacao_militar(self.database_manager, df)

    def insert_auditoria(self, cod_siafi, ano_auditoria):
        insert_auditoria(self.db, cod_siafi, ano_auditoria)

    def insert_execucao_licitacao(self, df):
        insert_execucao_licitacao(self.database_manager, df)
    
    def insert_pagamento(self, df):
        insert_pagamento(self.database_manager, df)

    def insert_patrimonio(self, df):
        insert_patrimonio(self.database_manager, df)

    def get_auditoria_statistics(self):
        """Obtém estatísticas das auditorias realizadas."""
        query = QSqlQuery(self.db)
        sql = """
        SELECT 
            om.cod_siafi,
            om.nome_om,
            COUNT(a.id_auditoria) AS total_auditorias,
            MAX(a.ano_auditoria) AS ultima_auditoria,
            (strftime('%Y', 'now') - MAX(a.ano_auditoria)) AS anos_desde_ultima
        FROM organizacoes_militares om
        LEFT JOIN auditorias a ON om.id_om = a.id_om
        GROUP BY om.id_om
        ORDER BY anos_desde_ultima DESC
        """
        query.prepare(sql)

        if not query.exec():
            print("Erro ao obter estatísticas de auditorias:", query.lastError().text())
            return []

        resultados = []
        while query.next():
            resultados.append({
                "cod_siafi": query.value(0),
                "nome_om": query.value(1),
                "total_auditorias": query.value(2),
                "ultima_auditoria": query.value(3),
                "anos_desde_ultima": query.value(4)
            })

        return resultados

class CustomSqlTableModel(QSqlTableModel):
    def __init__(self, parent=None, db=None, database_manager=None, non_editable_columns=None):
        super().__init__(parent, db)
        self.database_manager = database_manager
        self.non_editable_columns = non_editable_columns if non_editable_columns is not None else []
        
        # Define os nomes das colunas
        self.column_names = [
            "uasg", "descricao_om"            
        ]

    def flags(self, index):
        if index.column() in self.non_editable_columns:
            return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable  # Remove a permissão de edição
        return super().flags(index)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Verifica se estamos na coluna 'status'
        if index.column() == self.fieldIndex("status"):
            if role == Qt.ItemDataRole.DisplayRole:
                status_value = super().data(index, Qt.ItemDataRole.DisplayRole)  # Obtém valor do banco de dados
                if not status_value:  # Se estiver vazio ou None, substitui por "Planejamento"
                    # print(f"[DEBUG] Status vazio encontrado na linha {index.row()}. Definindo 'Planejamento'.")
                    return "Planejamento"
                return status_value  # Caso contrário, retorna o valor correto
            
        # Verifica se estamos na coluna 'dias'
        if index.column() == self.fieldIndex("dias"):
            if role == Qt.ItemDataRole.DisplayRole:
                # Obtém o índice e valor da coluna "vigencia_final"
                vigencia_final_index = self.fieldIndex("vigencia_final")
                vigencia_final = self.index(index.row(), vigencia_final_index).data()

                # print(f"[DEBUG] Vigência final obtida para a linha {index.row()}: {vigencia_final}")  # Debug print

                if vigencia_final:
                    try:
                        # Tenta converter 'DD/MM/YYYY'
                        vigencia_final_date = datetime.strptime(vigencia_final, '%d/%m/%Y')
                        # print(f"[DEBUG] Conversão bem-sucedida (DD/MM/YYYY): {vigencia_final_date}")  # Debug print
                    except ValueError:
                        try:
                            # Tenta converter 'YYYY-MM-DD'
                            vigencia_final_date = datetime.strptime(vigencia_final, '%Y-%m-%d')
                            # print(f"[DEBUG] Conversão bem-sucedida (YYYY-MM-DD): {vigencia_final_date}")  # Debug print
                        except ValueError:
                            # print(f"[ERRO] Falha ao converter data: {vigencia_final}. Formato inválido.")  # Debug print
                            return "Data Inválida"

                    # Calcula os dias restantes
                    hoje = datetime.today()
                    dias = (vigencia_final_date - hoje).days
                    # print(f"[DEBUG] Hoje: {hoje}, Vigência final: {vigencia_final_date}, Dias restantes: {dias}")  # Debug print
                    return dias  # Retorna os dias restantes

                else:
                    print(f"[ERRO] Sem data para calcular na linha {index.row()}")  # Debug print
                    return "Erro"

            elif role == Qt.ItemDataRole.ForegroundRole:
                # Obtém o valor da coluna 'dias' calculado anteriormente
                value = self.data(index, Qt.ItemDataRole.DisplayRole)
                if isinstance(value, int):  # Certifica-se de que é numérico
                    if value < 0:
                        return QColor(195, 195, 195)  # Cinza
                    elif 0 <= value < 30:
                        return QColor(255, 0, 0)  # Vermelho vivo
                    elif 30 <= value < 60:
                        return QColor(255, 140, 0)  # Laranja forte
                    elif 60 <= value < 90:
                        return QColor(255, 200, 0)  # Amarelo alaranjado
                    elif 90 <= value < 120:
                        return QColor(255, 255, 0)  # Amarelo vivo
                    elif 120 <= value < 180:
                        return QColor(173, 255, 47)  # Verde amarelado
                    elif 180 <= value < 360:
                        return QColor(50, 205, 50)  # Verde médio
                    elif value > 360:
                        return QColor(0, 150, 255)  # Azul vivo para valores maiores que 360

        # Coluna 'prorrogável' (Exemplo de outra coloração)
        if index.column() == self.fieldIndex("prorrogavel"):
            value = super().data(index, Qt.ItemDataRole.DisplayRole)
            if role == Qt.ItemDataRole.ForegroundRole:
                if value == "Sim":
                    return QColor(50, 205, 50)  # Verde
                elif value == "Não":
                    return QColor(255, 0, 0)  # Vermelho

        return super().data(index, role)
