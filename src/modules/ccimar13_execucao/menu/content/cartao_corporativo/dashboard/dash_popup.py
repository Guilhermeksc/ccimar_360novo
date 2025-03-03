from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, QLineEdit, QScrollArea
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

class DashboardPopup(QDialog): 
    def __init__(self, unique_orgaos, data_fetcher, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard - Cartão Corporativo")
        self.resize(800, 600)
        self.layout = QVBoxLayout(self)
        self.data_fetcher = data_fetcher  # Função para buscar dados do banco

        # Título
        self.title_label = QLabel("Selecione um órgão para visualizar os dados:", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Campo de busca para filtrar o ComboBox
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Digite para buscar um órgão...")
        self.search_box.textChanged.connect(self.filter_combobox)
        self.layout.addWidget(self.search_box)

        # ComboBox para selecionar o órgão
        self.orgao_combobox = QComboBox(self)
        self.orgao_items = []  # Lista para armazenar os itens originais
        self.orgao_data_map = {}  # Mapeia os textos para seus respectivos códigos
        
        for _, row in unique_orgaos.iterrows():
            cod_orgao = row['cod_orgao']
            nome_orgao = row['nome_orgao']
            item_text = f"{cod_orgao} - {nome_orgao}"
            self.orgao_combobox.addItem(item_text, cod_orgao)
            self.orgao_items.append(item_text)  # 🔹 Armazena apenas o texto para evitar erro
            self.orgao_data_map[item_text] = cod_orgao  # 🔹 Mapeia os códigos corretamente
        
        self.layout.addWidget(self.orgao_combobox)

        # Área de rolagem para os gráficos
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

        # Conectar o ComboBox para atualização de gráficos
        self.orgao_combobox.currentIndexChanged.connect(self.update_graphs)

        # Botão de fechar
        self.close_button = QPushButton("Fechar", self)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

    def update_graphs(self):
        """Atualiza os gráficos com base no órgão selecionado."""
        index = self.orgao_combobox.currentIndex()
        if index == -1:
            print("Nenhum órgão selecionado")
            return
        
        selected_text = self.orgao_combobox.currentText()
        selected_cod_orgao = self.orgao_data_map.get(selected_text, None)  # 🔹 Obtém o código do mapa
        print(f"Órgão selecionado: {selected_cod_orgao}")

        if not selected_cod_orgao:
            print("Nenhum código de órgão foi capturado corretamente")
            return

        self.clear_graphs()
        
        data = self.data_fetcher(selected_cod_orgao)
        if data is None or data.empty:
            print("Nenhum dado disponível para esse órgão")
            return
        
        self.add_bar_chart(data, 'nome_unidade_gestora', 'valor_transacao', 'Top 10 Valores por Unidade Gestora')
        self.add_bar_chart(data, 'nome_favorecido', 'valor_transacao', 'Top 10 Favorecidos')
        self.add_filtered_view(data, 'nome_favorecido', 'SEM INFORMACAO')

    def filter_combobox(self, text):
        """Filtra as opções do ComboBox com base no texto digitado pelo usuário."""
        self.orgao_combobox.clear()
        for item in self.orgao_items:
            if text.lower() in item.lower():  # 🔹 Agora item é uma string, evitando o erro
                self.orgao_combobox.addItem(item, self.orgao_data_map[item])  # 🔹 Adiciona os códigos corretamente

    def add_bar_chart(self, data, x_col, y_col, title):
        """Adiciona um gráfico de barras ao layout."""
        top10 = data.groupby(x_col)[y_col].sum().nlargest(10)
        fig, ax = plt.subplots()
        top10.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_ylabel(y_col)
        ax.set_xlabel(x_col)
        canvas = FigureCanvas(fig)
        self.scroll_layout.addWidget(canvas)

    def add_filtered_view(self, data, column, filter_value):
        """Cria uma visualização para os valores filtrados."""
        filtered_data = data[data[column] == filter_value]
        if filtered_data.empty:
            return
        
        label = QLabel(f"Registros com {column} = {filter_value}: {len(filtered_data)}", self)
        self.scroll_layout.addWidget(label)

    def clear_graphs(self):
        """Remove os gráficos existentes antes de adicionar novos."""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
