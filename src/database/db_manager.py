import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = self.connect_to_database()
        return self.connection

    def connect_to_database(self):
        try:
            connection = sqlite3.connect(self.db_path)
            return connection
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database at {self.db_path}: {e}")
            raise

    def execute_query(self, query, params=None):
        with self.connect_to_database() as conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            except sqlite3.Error as e:
                logging.error(f"Error executing query: {query}, Error: {e}")
                return None

    def execute_update(self, query, params=None):
        with self.connect_to_database() as conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Error executing update: {query}, Error: {e}")
                return False
            return True

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def fetch_all(self, query):
        """
        Executa uma consulta SQL e retorna todos os registros.
        
        :param query: A string de consulta SQL a ser executada.
        :return: Uma lista de dicionários, onde cada dicionário representa uma linha do resultado.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]  # Nomes das colunas
            rows = cursor.fetchall()
            # Converte cada linha em um dicionário com chaves sendo os nomes das colunas
            data = [dict(zip(columns, row)) for row in rows]
        return data

    def delete_data(self, id_processo):
        """Exclui um registro da tabela 'controle_planejamento' pelo id_processo."""
        query = "DELETE FROM controle_planejamento WHERE id_processo = ?"
        return self.execute_update(query, (id_processo,))
    
# def check_table_structure():
#     db = DatabaseManager("ccimar12.db")
#     table_info = db.execute_query("PRAGMA table_info(atas_detalhes);")

#     print("📌 Estrutura da tabela atas_detalhes:")
#     for col in table_info:
#         print(f" - {col[1]} ({col[2]})")  # Nome e tipo da coluna

# check_table_structure()    