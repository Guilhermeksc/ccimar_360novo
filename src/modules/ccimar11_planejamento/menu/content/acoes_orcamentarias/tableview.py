import os
import json
from pathlib import Path
import pandas as pd
import sqlite3
import logging
from PyQt6.QtWidgets import (
    QTableView, QMessageBox, QStyledItemDelegate,
)
from PyQt6.QtCore import Qt
from paths import OM_REPRESENTATIVAS_PATH

class CenteredDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

class CustomTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)
        self.setItemDelegate(CenteredDelegate(self))
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)

def load_config():
    if os.path.exists(OM_REPRESENTATIVAS_PATH):
        try:
            with open(OM_REPRESENTATIVAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao carregar a configuração: {e}")
            return None
    else:
        default_config = {
            "mapa_om_representativas": []
        }
        try:
            with open(OM_REPRESENTATIVAS_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao criar arquivo de configuração: {e}")
        return default_config

class CSVModelManager:
    def __init__(self, file_path, file_type='excel'):
        self.file_path = file_path
        self.sheets = {}


    def import_data(self, db_manager):
        sheet_name, df = list(self.sheets.items())[0]
        # Cria a tabela no banco usando o nome da aba (deve seguir o padrão YYYY_OrcamentoDespesa)
        table_name = self.create_table(db_manager, sheet_name)
        insert_sql = f"""
        INSERT INTO "{table_name}" (
            exercicio, codigo_orgao_superior, nome_orgao_superior,
            codigo_orgao_subordinado, nome_orgao_subordinado,
            codigo_unidade_orcamentaria, nome_unidade_orcamentaria,
            codigo_funcao, nome_funcao,
            codigo_subfuncao, nome_subfuncao,
            codigo_programa_orcamentario, nome_programa_orcamentario,
            codigo_acao, nome_acao,
            codigo_categoria_economica, nome_categoria_economica,
            codigo_grupo_despesa, nome_grupo_despesa,
            codigo_elemento_despesa, nome_elemento_despesa,
            orcamento_inicial, orcamento_atualizado,
            orcamento_empenhado, orcamento_realizado,
            percentual_realizado
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
        """
        for _, row in df.iterrows():
            try:
                percentual = float(row["% REALIZADO DO ORÇAMENTO (COM RELAÇÃO AO ORÇAMENTO ATUALIZADO)"])
            except:
                percentual = 0.0

            # Conversões similares para os demais valores numéricos...
            try:
                orcamento_inicial = float(row["ORÇAMENTO INICIAL (R$)"])
            except:
                orcamento_inicial = 0.0

            try:
                orcamento_atualizado = float(row["ORÇAMENTO ATUALIZADO (R$)"])
            except:
                orcamento_atualizado = 0.0

            try:
                orcamento_empenhado = float(row["ORÇAMENTO EMPENHADO (R$)"])
            except:
                orcamento_empenhado = 0.0

            try:
                orcamento_realizado = float(row["ORÇAMENTO REALIZADO (R$)"])
            except:
                orcamento_realizado = 0.0

            params = (
                str(row["EXERCÍCIO"]),
                str(row["CÓDIGO ÓRGÃO SUPERIOR"]),
                str(row["NOME ÓRGÃO SUPERIOR"]),
                str(row["CÓDIGO ÓRGÃO SUBORDINADO"]),
                str(row["NOME ÓRGÃO SUBORDINADO"]),
                str(row["CÓDIGO UNIDADE ORÇAMENTÁRIA"]),
                str(row["NOME UNIDADE ORÇAMENTÁRIA"]),
                str(row["CÓDIGO FUNÇÃO"]),
                str(row["NOME FUNÇÃO"]),
                str(row["CÓDIGO SUBFUNÇÃO"]),
                str(row["NOME SUBFUNÇÃO"]),
                str(row["CÓDIGO PROGRAMA ORÇAMENTÁRIO"]),
                str(row["NOME PROGRAMA ORÇAMENTÁRIO"]),
                str(row["CÓDIGO AÇÃO"]),
                str(row["NOME AÇÃO"]),
                str(row["CÓDIGO CATEGORIA ECONÔMICA"]),
                str(row["NOME CATEGORIA ECONÔMICA"]),
                str(row["CÓDIGO GRUPO DE DESPESA"]),
                str(row["NOME GRUPO DE DESPESA"]),
                str(row["CÓDIGO ELEMENTO DE DESPESA"]),
                str(row["NOME ELEMENTO DE DESPESA"]),
                orcamento_inicial,
                orcamento_atualizado,
                orcamento_empenhado,
                orcamento_realizado,
                percentual
            )
            db_manager.execute_update(insert_sql, params)

    def create_table(self, db_manager, sheet_name):
        # Define o nome da tabela fixo
        table_name = "orcamento_despesa"
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            exercicio TEXT,
            codigo_orgao_superior TEXT,
            nome_orgao_superior TEXT,s
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
        return table_name
