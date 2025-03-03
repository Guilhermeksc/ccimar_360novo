"""
Módulo para diálogos relacionados aos objetos auditáveis.

Este módulo contém classes de diálogos para interação com objetos auditáveis,
incluindo edição de multiplicadores, detalhes de objetos e visualização de critérios.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from .persistence import update_objeto_criterios, get_objeto_criterios

class DetalhesDialog(QDialog):
    """
    Diálogo para edição dos detalhes de um objeto auditável.
    """
    def __init__(self, row_data, criterios_manager, model, row_index, parent=None):
        """
        Inicializa o diálogo de detalhes.
        
        Args:
            row_data (list): Dados da linha do objeto
            criterios_manager: Gerenciador de critérios
            model: Modelo de dados
            row_index (int): Índice da linha no modelo
            parent (QWidget, optional): Widget pai. Padrão é None.
        """
        super().__init__(parent)
        self.setWindowTitle("Detalhes do Objeto Auditável")
        self.setModal(True)
        self.criterios_manager = criterios_manager
        self.model = model
        self.row_index = row_index
        
        # Obter o ID do objeto auditável (descrição)
        self.objeto_id = model.get_objeto_id(row_index)
        
        # Obter valores originais (se disponíveis)
        self.original_values = {
            "materialidade": model.data(model.index(row_index, 2), Qt.ItemDataRole.UserRole) or row_data[2],
            "relevancia": model.data(model.index(row_index, 3), Qt.ItemDataRole.UserRole) or row_data[3],
            "criticidade": model.data(model.index(row_index, 4), Qt.ItemDataRole.UserRole) or row_data[4]
        }
        
        # Configurar a interface
        self.setup_ui(row_data)
        
        # Definir valores iniciais
        self.set_initial_values()
        
        # Conectar sinais
        self.connect_signals()
    
    def setup_ui(self, row_data):
        """
        Configura a interface do diálogo.
        
        Args:
            row_data (list): Dados da linha do objeto
        """
        # Definir tamanho do diálogo
        self.resize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título do objeto
        title_label = QLabel(f"<b>{row_data[1]}</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(title_label)
        
        # Layout para os grupos de critérios
        criteria_layout = QHBoxLayout()
        
        # Grupo para Materialidade
        self.mat_group = QGroupBox(f"Materialidade (x{self.model.materialidade_peso})")
        mat_layout = QVBoxLayout(self.mat_group)
        
        # Obter critérios de materialidade
        materialidade_criterios = self.criterios_manager.get_criterios("materialidade")
        
        # Criar combos para cada critério de materialidade
        self.mat_combos = {}
        for criterio in materialidade_criterios:
            # Verificar se o critério é um dicionário
            if not isinstance(criterio, dict):
                continue
                
            # Criar layout para o critério
            criterio_layout = QFormLayout()
            
            # Criar combo para o critério
            combo = QComboBox()
            
            # Adicionar opções ao combo
            self.populate_combo(combo, criterio.get("opcoes", []))
            
            # Adicionar o combo ao layout
            criterio_layout.addRow(criterio.get("nome", ""), combo)
            
            # Adicionar o layout ao grupo
            mat_layout.addLayout(criterio_layout)
            
            # Armazenar o combo para acesso posterior
            criterio_id = criterio.get("id")
            if criterio_id:
                self.mat_combos[criterio_id] = combo
        
        criteria_layout.addWidget(self.mat_group)
        
        # Grupo para Relevância
        self.rel_group = QGroupBox(f"Relevância (x{self.model.relevancia_peso})")
        rel_layout = QVBoxLayout(self.rel_group)
        
        # Obter critérios de relevância
        relevancia_criterios = self.criterios_manager.get_criterios("relevancia")
        
        # Criar combos para cada critério de relevância
        self.rel_combos = {}
        for criterio in relevancia_criterios:
            # Verificar se o critério é um dicionário
            if not isinstance(criterio, dict):
                continue
                
            # Criar layout para o critério
            criterio_layout = QFormLayout()
            
            # Criar combo para o critério
            combo = QComboBox()
            
            # Adicionar opções ao combo
            self.populate_combo(combo, criterio.get("opcoes", []))
            
            # Adicionar o combo ao layout
            criterio_layout.addRow(criterio.get("nome", ""), combo)
            
            # Adicionar o layout ao grupo
            rel_layout.addLayout(criterio_layout)
            
            # Armazenar o combo para acesso posterior
            criterio_id = criterio.get("id")
            if criterio_id:
                self.rel_combos[criterio_id] = combo
        
        criteria_layout.addWidget(self.rel_group)
        
        # Grupo para Criticidade
        self.crit_group = QGroupBox(f"Criticidade (x{self.model.criticidade_peso})")
        crit_layout = QVBoxLayout(self.crit_group)
        
        # Obter critérios de criticidade
        criticidade_criterios = self.criterios_manager.get_criterios("criticidade")
        
        # Criar combos para cada critério de criticidade
        self.crit_combos = {}
        for criterio in criticidade_criterios:
            # Verificar se o critério é um dicionário
            if not isinstance(criterio, dict):
                continue
                
            # Criar layout para o critério
            criterio_layout = QFormLayout()
            
            # Criar combo para o critério
            combo = QComboBox()
            
            # Adicionar opções ao combo
            self.populate_combo(combo, criterio.get("opcoes", []))
            
            # Adicionar o combo ao layout
            criterio_layout.addRow(criterio.get("nome", ""), combo)
            
            # Adicionar o layout ao grupo
            crit_layout.addLayout(criterio_layout)
            
            # Armazenar o combo para acesso posterior
            criterio_id = criterio.get("id")
            if criterio_id:
                self.crit_combos[criterio_id] = combo
        
        criteria_layout.addWidget(self.crit_group)
        
        main_layout.addLayout(criteria_layout)
        
        # Grupo para Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QGridLayout(results_group)
        
        # Labels para os resultados
        self.mat_result_label = QLabel("0")
        self.rel_result_label = QLabel("0")
        self.crit_result_label = QLabel("0")
        self.total_result_label = QLabel("0")
        self.risco_result_label = QLabel("Baixo")
        
        # Adicionar labels ao layout
        results_layout.addWidget(QLabel("Materialidade:"), 0, 0)
        results_layout.addWidget(self.mat_result_label, 0, 1)
        
        results_layout.addWidget(QLabel("Relevância:"), 1, 0)
        results_layout.addWidget(self.rel_result_label, 1, 1)
        
        results_layout.addWidget(QLabel("Criticidade:"), 2, 0)
        results_layout.addWidget(self.crit_result_label, 2, 1)
        
        results_layout.addWidget(QLabel("Total:"), 3, 0)
        results_layout.addWidget(self.total_result_label, 3, 1)
        
        results_layout.addWidget(QLabel("Tipo de Risco:"), 4, 0)
        results_layout.addWidget(self.risco_result_label, 4, 1)
        
        main_layout.addWidget(results_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        # Botão Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancelar)
        
        # Botão Salvar
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self.save_changes)
        button_layout.addWidget(btn_salvar)
        
        main_layout.addLayout(button_layout)
    
    def populate_combo(self, combo, opcoes):
        """
        Popula um combo com opções.
        
        Args:
            combo (QComboBox): Combo a ser populado
            opcoes (list): Lista de opções
        """
        for opcao in opcoes:
            combo.addItem(opcao.get("descricao", ""), opcao)
    
    def set_initial_values(self):
        """
        Define os valores iniciais dos combos com base nos critérios do objeto.
        """
        # Função auxiliar para encontrar o índice da opção selecionada
        def find_option_index(combo, value):
            for i in range(combo.count()):
                if combo.itemText(i) == value:
                    return i
            return 0  # Retornar o primeiro item se não encontrar
        
        # Carregar critérios do objeto
        criterios = get_objeto_criterios(self.objeto_id) or {}
        
        # Definir valores para materialidade
        if isinstance(criterios, dict) and 'materialidade' in criterios and isinstance(criterios['materialidade'], dict):
            for criterio_id, valor in criterios['materialidade'].items():
                if criterio_id in self.mat_combos:
                    combo = self.mat_combos[criterio_id]
                    descricao = valor.get('descricao', '') if isinstance(valor, dict) else str(valor)
                    index = find_option_index(combo, descricao)
                    combo.setCurrentIndex(index)
        
        # Definir valores para relevância
        if isinstance(criterios, dict) and 'relevancia' in criterios and isinstance(criterios['relevancia'], dict):
            for criterio_id, valor in criterios['relevancia'].items():
                if criterio_id in self.rel_combos:
                    combo = self.rel_combos[criterio_id]
                    descricao = valor.get('descricao', '') if isinstance(valor, dict) else str(valor)
                    index = find_option_index(combo, descricao)
                    combo.setCurrentIndex(index)
        
        # Definir valores para criticidade
        if isinstance(criterios, dict) and 'criticidade' in criterios and isinstance(criterios['criticidade'], dict):
            for criterio_id, valor in criterios['criticidade'].items():
                if criterio_id in self.crit_combos:
                    combo = self.crit_combos[criterio_id]
                    descricao = valor.get('descricao', '') if isinstance(valor, dict) else str(valor)
                    index = find_option_index(combo, descricao)
                    combo.setCurrentIndex(index)
        
        # Atualizar os cálculos
        self.update_calculations()
    
    def connect_signals(self):
        """
        Conecta os sinais dos combos para atualizar os cálculos quando alterados.
        """
        # Conectar combos de materialidade
        for combo in self.mat_combos.values():
            combo.currentIndexChanged.connect(self.update_calculations)
        
        # Conectar combos de relevância
        for combo in self.rel_combos.values():
            combo.currentIndexChanged.connect(self.update_calculations)
        
        # Conectar combos de criticidade
        for combo in self.crit_combos.values():
            combo.currentIndexChanged.connect(self.update_calculations)
    
    def get_selected_value(self, combo):
        """
        Obtém o valor selecionado em um combo.
        
        Args:
            combo (QComboBox): Combo a ser consultado
            
        Returns:
            dict: Dados da opção selecionada
        """
        return combo.currentData()
    
    def update_calculations(self):
        """
        Atualiza os cálculos com base nos valores selecionados.
        """
        # Pesos para cada categoria
        materialidade_peso = self.model.materialidade_peso
        relevancia_peso = self.model.relevancia_peso
        criticidade_peso = self.model.criticidade_peso
        
        # Calcular materialidade
        materialidade_total = 0
        materialidade_max = 0
        
        for combo in self.mat_combos.values():
            opcao = self.get_selected_value(combo)
            if opcao:
                materialidade_total += opcao.get('pontuacao', 0)
                materialidade_max += 10  # Considerando que a pontuação máxima é 10
        
        # Normalizar materialidade para escala de 0 a 10
        materialidade = 0
        if materialidade_max > 0:
            materialidade = (materialidade_total / materialidade_max) * 10
        
        # Calcular relevância
        relevancia_total = 0
        relevancia_max = 0
        
        for combo in self.rel_combos.values():
            opcao = self.get_selected_value(combo)
            if opcao:
                relevancia_total += opcao.get('pontuacao', 0)
                relevancia_max += 10  # Considerando que a pontuação máxima é 10
        
        # Normalizar relevância para escala de 0 a 10
        relevancia = 0
        if relevancia_max > 0:
            relevancia = (relevancia_total / relevancia_max) * 10
        
        # Calcular criticidade
        criticidade_total = 0
        criticidade_max = 0
        
        for combo in self.crit_combos.values():
            opcao = self.get_selected_value(combo)
            if opcao:
                criticidade_total += opcao.get('pontuacao', 0)
                criticidade_max += 10  # Considerando que a pontuação máxima é 10
        
        # Normalizar criticidade para escala de 0 a 10
        criticidade = 0
        if criticidade_max > 0:
            criticidade = (criticidade_total / criticidade_max) * 10
        
        # Calcular total ponderado
        total = (materialidade * materialidade_peso) + (relevancia * relevancia_peso) + (criticidade * criticidade_peso)
        
        # Determinar tipo de risco
        tipo_risco = "Baixo"
        if total >= 80:
            tipo_risco = "Alto"
        elif total >= 50:
            tipo_risco = "Médio"
        
        # Atualizar labels
        self.mat_result_label.setText(f"{materialidade:.2f}")
        self.rel_result_label.setText(f"{relevancia:.2f}")
        self.crit_result_label.setText(f"{criticidade:.2f}")
        self.total_result_label.setText(f"{total:.2f}")
        self.risco_result_label.setText(tipo_risco)
    
    def get_highest_value_option(self, combos):
        """
        Obtém a opção com maior valor entre os combos.
        
        Args:
            combos (dict): Dicionário de combos
            
        Returns:
            tuple: (criterio_id, opcao) da opção com maior valor
        """
        max_value = -1
        max_criterio_id = None
        max_opcao = None
        
        for criterio_id, combo in combos.items():
            opcao = self.get_selected_value(combo)
            if opcao and opcao.get('pontuacao', 0) > max_value:
                max_value = opcao.get('pontuacao', 0)
                max_criterio_id = criterio_id
                max_opcao = opcao
        
        return max_criterio_id, max_opcao
    
    def save_changes(self):
        """
        Salva as alterações feitas no diálogo.
        """
        # Atualizar os cálculos uma última vez para garantir que tudo está atualizado
        self.update_calculations()
        
        # Obter valores atuais
        materialidade = float(self.mat_result_label.text())
        relevancia = float(self.rel_result_label.text())
        criticidade = float(self.crit_result_label.text())
        total = float(self.total_result_label.text())
        tipo_risco = self.risco_result_label.text()
        
        # Criar dicionário de critérios
        criterios = {
            'materialidade': {},
            'relevancia': {},
            'criticidade': {},
            'valores_calculados': {
                'materialidade': materialidade,
                'relevancia': relevancia,
                'criticidade': criticidade,
                'total': total,
                'tipo_risco': tipo_risco
            }
        }
        
        # Adicionar critérios de materialidade
        for criterio_id, combo in self.mat_combos.items():
            opcao = self.get_selected_value(combo)
            if opcao:
                criterios['materialidade'][criterio_id] = {
                    'descricao': combo.currentText(),
                    'pontuacao': opcao.get('pontuacao', 0)
                }
        
        # Adicionar critérios de relevância
        for criterio_id, combo in self.rel_combos.items():
            opcao = self.get_selected_value(combo)
            if opcao:
                criterios['relevancia'][criterio_id] = {
                    'descricao': combo.currentText(),
                    'pontuacao': opcao.get('pontuacao', 0)
                }
        
        # Adicionar critérios de criticidade
        for criterio_id, combo in self.crit_combos.items():
            opcao = self.get_selected_value(combo)
            if opcao:
                criterios['criticidade'][criterio_id] = {
                    'descricao': combo.currentText(),
                    'pontuacao': opcao.get('pontuacao', 0)
                }
        
        # Salvar critérios
        update_objeto_criterios(self.objeto_id, criterios)
        
        # Atualizar o modelo
        self.model.setData(self.model.index(self.row_index, 2), str(materialidade))
        self.model.setData(self.model.index(self.row_index, 3), str(relevancia))
        self.model.setData(self.model.index(self.row_index, 4), str(criticidade))
        self.model.setData(self.model.index(self.row_index, 5), str(total))
        self.model.setData(self.model.index(self.row_index, 6), tipo_risco)
        
        # Armazenar os valores originais como UserRole
        self.model.setData(self.model.index(self.row_index, 2), materialidade, Qt.ItemDataRole.UserRole)
        self.model.setData(self.model.index(self.row_index, 3), relevancia, Qt.ItemDataRole.UserRole)
        self.model.setData(self.model.index(self.row_index, 4), criticidade, Qt.ItemDataRole.UserRole)
        
        # Fechar o diálogo
        self.accept()

class CriteriosViewDialog(QDialog):
    """
    Diálogo para visualização de critérios.
    """
    def __init__(self, criterios_manager, tipo, parent=None):
        """
        Inicializa o diálogo de visualização de critérios.
        
        Args:
            criterios_manager: Gerenciador de critérios
            tipo (str): Tipo de critério (materialidade, relevancia, criticidade)
            parent (QWidget, optional): Widget pai. Padrão é None.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Visualização de Critérios - {tipo.title()}")
        self.setModal(True)
        self.resize(600, 400)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Criar uma tabela para mostrar os critérios
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Critério", "Descrição", "Pontuação"])
        
        # Configurar a tabela
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Obter critérios do tipo especificado
        criterios = criterios_manager.get_criterios(tipo)
        
        # Variável para contar o número total de linhas
        total_rows = 0
        
        # Para cada critério, adicionar suas opções à tabela
        for criterio in criterios:
            # Verificar se o critério é um dicionário
            if not isinstance(criterio, dict):
                # Se for uma string, adicionar como critério simples
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(criterio))
                table.setItem(row, 1, QTableWidgetItem(""))
                table.setItem(row, 2, QTableWidgetItem("0"))
                total_rows += 1
                continue
                
            criterio_nome = criterio.get("nome", "")
            
            # Para cada opção do critério
            opcoes = criterio.get("opcoes", [])
            if not opcoes:
                # Se não houver opções, adicionar apenas o critério
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(criterio_nome))
                table.setItem(row, 1, QTableWidgetItem(""))
                table.setItem(row, 2, QTableWidgetItem("0"))
                total_rows += 1
            else:
                # Para cada opção do critério
                for opcao in opcoes:
                    # Adicionar uma linha à tabela
                    row = table.rowCount()
                    table.insertRow(row)
                    
                    # Adicionar os itens à linha
                    table.setItem(row, 0, QTableWidgetItem(criterio_nome))
                    table.setItem(row, 1, QTableWidgetItem(opcao.get("descricao", "")))
                    table.setItem(row, 2, QTableWidgetItem(str(opcao.get("pontuacao", 0))))
                    
                    # Incrementar o contador de linhas
                    total_rows += 1
        
        # Adicionar a tabela ao layout
        layout.addWidget(table)
        
        # Botão para fechar o diálogo
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)
        
        # Ajustar o tamanho da tabela
        table.resizeRowsToContents()
        
        # Ajustar o tamanho do diálogo com base no número de linhas
        self.resize(600, min(400, 100 + total_rows * 30)) 