from PyQt6.QtCore import QObject, Qt
import logging
from database.db_manager import DatabaseManager
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtGui import QColor
import sqlite3
from datetime import datetime
import pandas as pd

class CartaoCorporativoModel(QObject):
    def __init__(self, database_path, parent=None):
        super().__init__(parent)
        self.database_manager = DatabaseManager(database_path)
        self.db = None  # Atributo para o banco de dados
        self.model = None  # Atributo para o modelo SQL
        self.init_database()  # Inicializa a conexão e a estrutura do banco de dados

    def init_database(self):
        """Inicializa a conexão com o banco de dados e ajusta a estrutura da tabela."""
        if QSqlDatabase.contains("cartao_corporativo_conn"):
            QSqlDatabase.removeDatabase("cartao_corporativo_conn")
        self.db = QSqlDatabase.addDatabase('QSQLITE', "cartao_corporativo_conn")
        self.db.setDatabaseName(str(self.database_manager.db_path))

        if not self.db.open():
            raise Exception("Não foi possível abrir a conexão com o banco de dados.")

        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Cria a tabela 'tabela_cartao_corporativo' com a estrutura definida, caso ainda não exista."""
        query = QSqlQuery(self.db)
        if not query.exec("""
            CREATE TABLE IF NOT EXISTS tabela_cartao_corporativo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_orgao_superior INTEGER,
                nome_orgao_superior TEXT,
                cod_orgao INTEGER,
                nome_orgao TEXT,
                cod_unidade_gestora INTEGER,
                nome_unidade_gestora TEXT,
                ano_extrato INTEGER,
                mes_extrato INTEGER,
                cpf_portador TEXT,
                nome_portador TEXT,
                cnpj_cpf_favorecido TEXT,
                nome_favorecido TEXT,
                transacao TEXT,
                data_transacao DATE,
                valor_transacao REAL
            )
        """):
            logging.error("Falha ao criar a tabela 'tabela_cartao_corporativo': %s", query.lastError().text())
        else:
            logging.info("Tabela 'tabela_cartao_corporativo' criada com sucesso.")

    def setup_model(self, table_name="tabela_cartao_corporativo", editable=False):
        """Configura o modelo SQL para a tabela especificada."""

        if not self.db:
            raise Exception("Banco de dados não inicializado!")

        # 🔹 Configura o modelo como um `CustomSqlTableModel`
        self.model = CustomSqlTableModel(
            parent=self,
            db=self.db,
            database_manager=self.database_manager,
            non_editable_columns=[0, 4, 8, 10, 13]  # Ajuste conforme necessário
        )
        
        self.model.setTable(table_name)

        # 🔹 Define a estratégia de edição
        if editable:
            self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        self.model.select()
        return self.model

    def get_data(self):
        """Retorna todos os dados da tabela 'tabela_cartao_corporativo'."""
        return self.database_manager.fetch_all("SELECT * FROM tabela_cartao_corporativo")

    def insert_or_update_data(self, data):
        """Insere ou atualiza um registro na tabela 'tabela_cartao_corporativo'."""
        logging.info("Dados recebidos para salvar: %s", data)

        upsert_sql = '''
        INSERT INTO tabela_cartao_corporativo (
            cod_orgao_superior, nome_orgao_superior, cod_orgao, nome_orgao, cod_unidade_gestora, 
            nome_unidade_gestora, ano_extrato, mes_extrato, cpf_portador, nome_portador, 
            cnpj_cpf_favorecido, nome_favorecido, transacao, data_transacao, valor_transacao
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        ) ON CONFLICT(id) DO UPDATE SET
            cod_orgao_superior=excluded.cod_orgao_superior, 
            nome_orgao_superior=excluded.nome_orgao_superior, 
            cod_orgao=excluded.cod_orgao, 
            nome_orgao=excluded.nome_orgao, 
            cod_unidade_gestora=excluded.cod_unidade_gestora, 
            nome_unidade_gestora=excluded.nome_unidade_gestora, 
            ano_extrato=excluded.ano_extrato, 
            mes_extrato=excluded.mes_extrato, 
            cpf_portador=excluded.cpf_portador, 
            nome_portador=excluded.nome_portador, 
            cnpj_cpf_favorecido=excluded.cnpj_cpf_favorecido, 
            nome_favorecido=excluded.nome_favorecido, 
            transacao=excluded.transacao, 
            data_transacao=excluded.data_transacao, 
            valor_transacao=excluded.valor_transacao
        '''

        try:
            with self.database_manager as conn:
                cursor = conn.cursor()
                cursor.execute(upsert_sql, (
                    data.get('cod_orgao_superior'), data.get('nome_orgao_superior'), data.get('cod_orgao'), data.get('nome_orgao'),
                    data.get('cod_unidade_gestora'), data.get('nome_unidade_gestora'), data.get('ano_extrato'), data.get('mes_extrato'),
                    data.get('cpf_portador'), data.get('nome_portador'), data.get('cnpj_cpf_favorecido'), data.get('nome_favorecido'),
                    data.get('transacao'), data.get('data_transacao'), data.get('valor_transacao')
                ))
                conn.commit()
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                logging.warning("A tabela 'tabela_cartao_corporativo' não existe. Criando...")
                self.create_table_if_not_exists()
            else:
                logging.error("Erro ao tentar salvar os dados: %s", str(e))

    def get_all_model_data(self):
        """Obtém todos os dados da tabela 'tabela_cartao_corporativo'."""
        query = QSqlQuery(self.db)
        query.exec("SELECT * FROM tabela_cartao_corporativo")  # 🔹 Certifique-se de usar o nome correto da tabela

        data_list = []
        column_count = query.record().count()  # Obtém o número de colunas
        column_names = [query.record().fieldName(i) for i in range(column_count)]  # Obtém os nomes das colunas

        while query.next():
            row_data = {column_names[i]: query.value(i) for i in range(column_count)}
            data_list.append(row_data)

        return data_list

    def get_data_for_orgao(self, cod_orgao):
        """Retorna os dados filtrados para um determinado órgão."""
        query = """
            SELECT nome_unidade_gestora, valor_transacao, nome_favorecido 
            FROM tabela_cartao_corporativo 
            WHERE cod_orgao = ?
        """
        conn = sqlite3.connect(self.database_manager.db_path)
        df = pd.read_sql(query, conn, params=(cod_orgao,))
        conn.close()
        return df



class CustomSqlTableModel(QSqlTableModel):
    def __init__(self, parent=None, db=None, database_manager=None, non_editable_columns=None):
        super().__init__(parent, db)
        self.database_manager = database_manager
        self.non_editable_columns = non_editable_columns if non_editable_columns is not None else []

        # 🔹 Mantém referência às colunas da tabela
        self.column_names = [
            "id", "cod_orgao_superior", "nome_orgao_superior", "cod_orgao", "nome_orgao",
            "cod_unidade_gestora", "nome_unidade_gestora", "ano_extrato", "mes_extrato",
            "cpf_portador", "nome_portador", "cnpj_cpf_favorecido", "nome_favorecido",
            "transacao", "data_transacao", "valor_transacao"
        ]

        # 🔹 Configura a tabela e carrega os dados
        self.setTable("tabela_cartao_corporativo")
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.select()

    def flags(self, index):
        """Define permissões de edição para colunas específicas."""
        if index.column() in self.non_editable_columns:
            return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable  # Remove a permissão de edição
        return super().flags(index)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Personaliza a exibição dos dados, incluindo coloração dinâmica."""
        if not index.isValid():
            return None

        # 🔹 Formata valores da coluna "valor_transacao"
        if index.column() == self.column_names.index("valor_transacao"):
            if role == Qt.ItemDataRole.DisplayRole:
                valor = super().data(index, Qt.ItemDataRole.DisplayRole)
                return f"R$ {float(valor):,.2f}" if valor else "R$ 0,00"

        # 🔹 Coloração condicional para "valor_transacao"
        if index.column() == self.column_names.index("valor_transacao"):
            if role == Qt.ItemDataRole.ForegroundRole:
                valor = float(super().data(index, Qt.ItemDataRole.DisplayRole) or 0)
                if valor > 1000:
                    return QColor(255, 0, 0)  # Vermelho para valores altos
                elif valor < 50:
                    return QColor(0, 128, 0)  # Verde para valores baixos

        return super().data(index, role)

    def refresh(self):
        """🔄 Atualiza a visualização do modelo sem recriar o objeto."""
        self.select()