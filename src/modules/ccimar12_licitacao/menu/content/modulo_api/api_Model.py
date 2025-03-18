from PyQt6.QtCore import QObject, Qt
import logging
from database.db_manager import DatabaseManager
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtGui import QColor
import sqlite3
import pandas as pd

class APIModel(QObject):
    def __init__(self, database_path, parent=None):
        super().__init__(parent)
        self.database_manager = DatabaseManager(database_path)
        self.db = None
        self.model = None
        self.init_database()

    def init_database(self):
        """Inicializa a conexão com o banco de dados."""
        if QSqlDatabase.contains("licitacao_conn"):
            QSqlDatabase.removeDatabase("licitacao_conn")
        self.db = QSqlDatabase.addDatabase('QSQLITE', "licitacao_conn")
        self.db.setDatabaseName(str(self.database_manager.db_path))

        if not self.db.open():
            raise Exception("Não foi possível abrir a conexão com o banco de dados.")

        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Cria a tabela 'licitacao' se não existir."""
        query = QSqlQuery(self.db)
        query.exec("""
            CREATE TABLE IF NOT EXISTS licitacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unidade_responsavel TEXT,
                uasg INTEGER,
                id_item_pca INTEGER,
                categoria_item TEXT,
                id_futura_contratacao TEXT,
                nome_futura_contratacao TEXT,
                catalogo_utilizado TEXT,
                classificacao_catalogo TEXT,
                codigo_classificacao_superior INTEGER,
                nome_classificacao_superior TEXT,
                codigo_pdm_item INTEGER,
                nome_pdm_item TEXT,
                codigo_item INTEGER,
                descricao_item TEXT,
                unidade_fornecimento TEXT,
                quantidade_estimada INTEGER,
                valor_unitario_estimado REAL,
                valor_total_estimado REAL,
                valor_orcamentario_estimado REAL,
                data_desejada DATE
            )
        """)

    def setup_model(self, table_name="licitacao", editable=False):
        """Configura o modelo SQL."""
        if not self.db:
            raise Exception("Banco de dados não inicializado!")

        self.model = CustomSqlTableModel(parent=self, db=self.db, database_manager=self.database_manager)
        self.model.setTable(table_name)
        if editable:
            self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
        return self.model

    def insert_or_update_data(self, data):
        """Insere ou atualiza um registro na tabela."""
        upsert_sql = '''
        INSERT INTO licitacao (
            unidade_responsavel, uasg, id_item_pca, categoria_item, id_futura_contratacao, 
            nome_futura_contratacao, catalogo_utilizado, classificacao_catalogo, 
            codigo_classificacao_superior, nome_classificacao_superior, codigo_pdm_item, nome_pdm_item, 
            codigo_item, descricao_item, unidade_fornecimento, quantidade_estimada, 
            valor_unitario_estimado, valor_total_estimado, valor_orcamentario_estimado, data_desejada
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        ) ON CONFLICT(id) DO UPDATE SET
            unidade_responsavel=excluded.unidade_responsavel,
            uasg=excluded.uasg,
            id_item_pca=excluded.id_item_pca,
            categoria_item=excluded.categoria_item,
            id_futura_contratacao=excluded.id_futura_contratacao,
            nome_futura_contratacao=excluded.nome_futura_contratacao,
            catalogo_utilizado=excluded.catalogo_utilizado,
            classificacao_catalogo=excluded.classificacao_catalogo,
            codigo_classificacao_superior=excluded.codigo_classificacao_superior,
            nome_classificacao_superior=excluded.nome_classificacao_superior,
            codigo_pdm_item=excluded.codigo_pdm_item,
            nome_pdm_item=excluded.nome_pdm_item,
            codigo_item=excluded.codigo_item,
            descricao_item=excluded.descricao_item,
            unidade_fornecimento=excluded.unidade_fornecimento,
            quantidade_estimada=excluded.quantidade_estimada,
            valor_unitario_estimado=excluded.valor_unitario_estimado,
            valor_total_estimado=excluded.valor_total_estimado,
            valor_orcamentario_estimado=excluded.valor_orcamentario_estimado,
            data_desejada=excluded.data_desejada
        '''
        try:
            with self.database_manager as conn:
                cursor = conn.cursor()
                cursor.execute(upsert_sql, (
                    data.get('unidade_responsavel'), data.get('uasg'), data.get('id_item_pca'),
                    data.get('categoria_item'), data.get('id_futura_contratacao'), data.get('nome_futura_contratacao'),
                    data.get('catalogo_utilizado'), data.get('classificacao_catalogo'),
                    data.get('codigo_classificacao_superior'), data.get('nome_classificacao_superior'),
                    data.get('codigo_pdm_item'), data.get('nome_pdm_item'), data.get('codigo_item'), data.get('descricao_item'),
                    data.get('unidade_fornecimento'), data.get('quantidade_estimada'), data.get('valor_unitario_estimado'),
                    data.get('valor_total_estimado'), data.get('valor_orcamentario_estimado'), data.get('data_desejada')
                ))
                conn.commit()
        except sqlite3.OperationalError as e:
            logging.error("Erro ao tentar salvar os dados: %s", str(e))

class CustomSqlTableModel(QSqlTableModel):
    def __init__(self, parent=None, db=None, database_manager=None):
        super().__init__(parent, db)
        self.database_manager = database_manager
        self.setTable("licitacao")
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.select()

    def flags(self, index):
        """Define permissões de edição."""
        return super().flags(index)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Personaliza a exibição dos dados."""
        if not index.isValid():
            return None
        if index.column() == 17:  # valor_unitario_estimado
            if role == Qt.ItemDataRole.DisplayRole:
                valor = super().data(index, Qt.ItemDataRole.DisplayRole)
                return f"R$ {float(valor):,.2f}" if valor else "R$ 0,00"
        return super().data(index, role)

    def refresh(self):
        """Atualiza o modelo."""
        self.select()
