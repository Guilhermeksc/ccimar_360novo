from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget,
    QLineEdit, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

class DashboardPopup(QDialog): 
    def __init__(self, unique_orgaos, data_fetcher, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard - Cartão Corporativo")

        # 🔹 Definir tamanho mínimo para evitar erros de redimensionamento
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
        self.layout = QVBoxLayout(self)
        self.data_fetcher = data_fetcher  # Função para buscar dados do banco

        # Título
        self.title_label = QLabel("Selecione um órgão para visualizar os dados:", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Campo de busca e ComboBox
        self.orgao_combobox = QComboBox(self)
        self.orgao_data_map = {}
        for _, row in unique_orgaos.iterrows():
            item_text = f"{row['cod_orgao']} - {row['nome_orgao']}"
            self.orgao_combobox.addItem(item_text, row['cod_orgao'])
            self.orgao_data_map[item_text] = row['cod_orgao']
        
        self.layout.addWidget(self.orgao_combobox)

        # Criar o frame com barra de rolagem
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_frame = QFrame()
        self.scroll_layout = QVBoxLayout(self.scroll_frame)
        self.scroll_area.setWidget(self.scroll_frame)
        self.layout.addWidget(self.scroll_area)

        # Conectar evento de seleção do ComboBox
        self.orgao_combobox.currentIndexChanged.connect(self.update_graphs)

        # Botão de fechar
        self.close_button = QPushButton("Fechar", self)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

    def update_graphs(self):
        """Atualiza os gráficos e listas com base no órgão selecionado."""
        index = self.orgao_combobox.currentIndex()
        if index == -1:
            return

        selected_text = self.orgao_combobox.currentText()
        selected_cod_orgao = self.orgao_data_map.get(selected_text, None)

        if not selected_cod_orgao:
            return

        # Limpa os gráficos e listas antes de adicionar novos
        self.clear_graphs()

        # Obtém os dados do banco
        data = self.data_fetcher(selected_cod_orgao)
        if data is None or data.empty:
            return

        # Layout principal (grade para organizar elementos)
        main_layout = QGridLayout()

        # Criar layout horizontal para gráfico e lista de unidades gestoras
        graph_list_layout = QHBoxLayout()

        # Adiciona gráfico "Top 10 Valores por Unidade Gestora"
        self.add_bar_chart(data, 'cod_unidade_gestora', 'valor_transacao', 'Top 10 Valores por Unidade Gestora', graph_list_layout)

        # Adiciona a lista "Top 10 Unidades Gestoras"
        self.add_top_units_list(data, 'cod_unidade_gestora', 'valor_transacao', graph_list_layout)

        # Adiciona o layout de gráfico + lista na grade
        main_layout.addLayout(graph_list_layout, 0, 0)

        # Criar layout para a lista de favorecidos (embaixo)
        favored_layout = QVBoxLayout()
        self.add_favored_list(data, 'nome_favorecido', 'valor_transacao', favored_layout)

        # Adiciona a lista de favorecidos na grade
        main_layout.addLayout(favored_layout, 1, 0)

        # Adiciona a grade ao scroll_layout
        self.scroll_layout.addLayout(main_layout)

    def add_bar_chart(self, data, x_col, y_col, title, parent_layout):
        """Adiciona um gráfico de barras ao layout fornecido."""
        if x_col not in data.columns or y_col not in data.columns:
            return
        
        top10 = data.groupby(x_col)[y_col].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        top10.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_ylabel("Valor Transação (R$)")
        ax.set_xlabel("Unidade Gestora")
        
        canvas = FigureCanvas(fig)
        parent_layout.addWidget(canvas)

    def add_top_units_list(self, data, code_col, value_col, parent_layout):
        """Cria uma lista das 10 unidades gestoras com maior valor de transação."""
        if code_col not in data.columns or value_col not in data.columns:
            return

        top10 = data.groupby(code_col)[value_col].sum().nlargest(10)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Adiciona título
        title_label = QLabel("Top 10 Unidades Gestoras", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)

        # Adiciona itens da lista
        for code, value in top10.items():
            label = QLabel(f"UG {code}: R$ {value:,.2f}", self)
            layout.addWidget(label)

        parent_layout.addWidget(widget)

    def add_favored_list(self, data, name_col, value_col, parent_layout):
        """Cria uma lista dos 10 principais favorecidos com seus valores transacionados."""
        if name_col not in data.columns or value_col not in data.columns:
            return

        top10 = data.groupby(name_col)[value_col].sum().nlargest(10)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Adiciona título
        title_label = QLabel("Top 10 Favorecidos", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)

        # Adiciona itens da lista
        for name, value in top10.items():
            label = QLabel(f"{name}: R$ {value:,.2f}", self)
            layout.addWidget(label)

        parent_layout.addWidget(widget)

    def clear_graphs(self):
        """Remove os gráficos e listas anteriores antes de adicionar novos."""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
