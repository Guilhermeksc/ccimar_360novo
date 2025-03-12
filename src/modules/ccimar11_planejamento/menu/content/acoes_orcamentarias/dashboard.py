from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QWidget
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def apply_edit_dialog_style(dialog):
    """Aplica o estilo ao QDialog e seus componentes."""
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1E2E;
            color: #FFFFFF;
            font-size: 16px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 16px;
        }
        QLineEdit {
            background-color: #FFFFFF;
            font-size: 16px;
        }
        QTabWidget::pane {
            border: 1px solid #3D3D5C;
            background-color: #2D2D44;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #3D3D5C;
            color: #FFFFFF;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #5D5D8C;
            font-weight: bold;
        }
        QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            font-size: 16px;
        }
        QPushButton {
            background-color: #3CB500;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #60DE65;
        }
        QPushButton:pressed {
            background-color: #60DE65;
        }
        QPushButton[text="Cancelar"] {
            background-color: #f44336;
        }
        QPushButton[text="Cancelar"]:hover {
            background-color: #F56E6E;
        }
    """)

class DashboardDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard - Gráficos")
        self.resize(900, 600)
        self.db_manager = db_manager

        # Aplica CSS
        apply_edit_dialog_style(self)

        # Layout principal do QDialog
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # QTabWidget para agrupar as abas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Cria e adiciona a aba 1 (Análise via Combos)
        self.tab_analysis = QWidget()
        self.tab_widget.addTab(self.tab_analysis, "Análise Personalizada")
        self.setup_tab_analysis()

        # Cria e adiciona a aba 2 (Exemplo de outra análise)
        self.tab_secondary = QWidget()
        self.tab_widget.addTab(self.tab_secondary, "Comparativo Geral")
        self.setup_tab_secondary()

        # Cria e adiciona a aba 3 (pode adicionar quantas quiser)
        self.tab_third = QWidget()
        self.tab_widget.addTab(self.tab_third, "Outros Insights")
        self.setup_tab_third()

    # ---------------------------------------------
    # ABA 1: Análise usando combos e um gráfico
    # ---------------------------------------------
    def setup_tab_analysis(self):
        """Configura a primeira aba, com os combos e o gráfico."""
        layout = QHBoxLayout(self.tab_analysis)
        self.tab_analysis.setLayout(layout)

        # Lado esquerdo: Combos e botão
        self.selection_widget = QWidget()
        self.selection_layout = QVBoxLayout(self.selection_widget)
        self.selection_widget.setLayout(self.selection_layout)

        layout.addWidget(self.selection_widget)

        # Combo 1
        self.combo_orgao_subordinado = QComboBox()
        self.combo_orgao_subordinado.setPlaceholderText("Selecione o Órgão Subordinado")
        self.selection_layout.addWidget(QLabel("Órgão Subordinado:"))
        self.selection_layout.addWidget(self.combo_orgao_subordinado)

        # Combo 2
        self.combo_acao = QComboBox()
        self.combo_acao.setEnabled(False)
        self.combo_acao.setPlaceholderText("Selecione a Ação")
        self.selection_layout.addWidget(QLabel("Ação:"))
        self.selection_layout.addWidget(self.combo_acao)

        # Combo 3
        self.combo_categoria_economica = QComboBox()
        self.combo_categoria_economica.setEnabled(False)
        self.combo_categoria_economica.setPlaceholderText("Selecione o Elemento de Despesa")
        self.selection_layout.addWidget(QLabel("Elemento de Despesa:"))
        self.selection_layout.addWidget(self.combo_categoria_economica)

        # Botão gerar gráfico
        self.btn_gerar_grafico = QPushButton("Gerar Gráfico")
        self.btn_gerar_grafico.setEnabled(False)
        self.selection_layout.addWidget(self.btn_gerar_grafico)

        # Área do gráfico
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Conexões
        self.populate_combo_orgao()
        self.combo_orgao_subordinado.currentIndexChanged.connect(self.on_orgao_selected)
        self.combo_acao.currentIndexChanged.connect(self.on_acao_selected)
        self.combo_categoria_economica.currentIndexChanged.connect(self.on_categoria_selected)
        self.btn_gerar_grafico.clicked.connect(self.update_chart)

    def populate_combo_orgao(self):
        """Busca todos os 'nome_orgao_subordinado' no banco e adiciona ao combo."""
        if not self.db_manager:
            return
        query = """
            SELECT DISTINCT nome_orgao_subordinado
            FROM orcamento_despesa
            WHERE nome_orgao_subordinado <> ''
            ORDER BY nome_orgao_subordinado
        """
        results = self.db_manager.fetch_all(query)
        self.combo_orgao_subordinado.clear()
        self.combo_orgao_subordinado.addItem("Selecione...")
        for row in results:
            # Se fetch_all retorna dicionário:
            # self.combo_orgao_subordinado.addItem(row["nome_orgao_subordinado"])
            # Se retorna tupla:
            self.combo_orgao_subordinado.addItem(row["nome_orgao_subordinado"])


    def on_orgao_selected(self):
        orgao = self.combo_orgao_subordinado.currentText()
        if orgao == "Selecione...":
            self.combo_acao.setEnabled(False)
            self.combo_acao.clear()
            self.combo_categoria_economica.setEnabled(False)
            self.combo_categoria_economica.clear()
            self.btn_gerar_grafico.setEnabled(False)
            return

        # Preenche combo_acao
        self.combo_acao.setEnabled(True)
        query = """
            SELECT DISTINCT nome_acao
            FROM orcamento_despesa
            WHERE nome_orgao_subordinado = ?
              AND nome_acao <> ''
            ORDER BY nome_acao
        """
        results = self.db_manager.execute_query(query, (orgao,))
        self.combo_acao.clear()
        self.combo_acao.addItem("Selecione...")
        for row in results:
            # row é algo como ("VALOR_1", ) ou ("VALOR_1", "VALOR_2", ...)
            valor = row[0]  # em vez de row["coluna"]
            self.combo_acao.addItem(valor)

        # Limpa o combo de categoria e desabilita
        self.combo_categoria_economica.clear()
        self.combo_categoria_economica.setEnabled(False)
        self.btn_gerar_grafico.setEnabled(False)

    def on_acao_selected(self):
        acao = self.combo_acao.currentText()
        if acao == "Selecione...":
            self.combo_categoria_economica.setEnabled(False)
            self.combo_categoria_economica.clear()
            self.btn_gerar_grafico.setEnabled(False)
            return

        # Preenche combo_categoria_economica (ou elemento de despesa)
        self.combo_categoria_economica.setEnabled(True)
        orgao = self.combo_orgao_subordinado.currentText()
        query = """
            SELECT DISTINCT nome_elemento_despesa
            FROM orcamento_despesa
            WHERE nome_orgao_subordinado = ?
              AND nome_acao = ?
              AND nome_elemento_despesa <> ''
            ORDER BY nome_elemento_despesa
        """
        results = self.db_manager.execute_query(query, (orgao, acao))
        self.combo_categoria_economica.clear()
        self.combo_categoria_economica.addItem("Selecione...")
        
        for row in results:
            # row vem como tupla (ex.: ("Elemento X",))
            valor_categoria = row[0] if row else ""
            self.combo_categoria_economica.addItem(valor_categoria)


        self.btn_gerar_grafico.setEnabled(False)

    def on_categoria_selected(self):
        """Habilita o botão de gerar gráfico após a seleção do 3º combo."""
        categoria = self.combo_categoria_economica.currentText()
        if categoria == "Selecione...":
            self.btn_gerar_grafico.setEnabled(False)
        else:
            self.btn_gerar_grafico.setEnabled(True)

    def update_chart(self):
        """
        Gráfico: Orçamento Atualizado (barras) x Empenhado e Realizado (linhas)
        por exercício.
        """
        orgao = self.combo_orgao_subordinado.currentText()
        acao = self.combo_acao.currentText()
        categoria = self.combo_categoria_economica.currentText()

        if any(x == "Selecione..." for x in [orgao, acao, categoria]):
            return

        query = """
            SELECT exercicio,
                   orcamento_atualizado,
                   orcamento_empenhado,
                   orcamento_realizado
            FROM orcamento_despesa
            WHERE nome_orgao_subordinado = ?
              AND nome_acao = ?
              AND nome_elemento_despesa = ?
            ORDER BY exercicio
        """
        results = self.db_manager.execute_query(query, (orgao, acao, categoria))

        # year_data[ano] = {"atualizado": soma, "empenhado": soma, "realizado": soma}
        year_data = {}
        for row in results:
            ano = row["exercicio"]  # exercicio
            if ano not in year_data:
                year_data[ano] = {"atualizado": 0, "empenhado": 0, "realizado": 0}
            year_data[ano]["atualizado"] += row[1]
            year_data[ano]["empenhado"]  += row[2]
            year_data[ano]["realizado"]  += row[3]

        sorted_years = sorted(year_data.keys())
        if not sorted_years:
            return

        val_atualizado = [year_data[ano]["atualizado"] for ano in sorted_years]
        val_empenhado  = [year_data[ano]["empenhado"]  for ano in sorted_years]
        val_realizado  = [year_data[ano]["realizado"]  for ano in sorted_years]

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        indices = np.arange(len(sorted_years))
        bar_width = 0.6

        # Barras: orçamento atualizado
        ax.bar(indices, val_atualizado, bar_width, label="Atualizado")

        # Linhas: empenhado e realizado
        ax.plot(indices, val_empenhado,  marker='o', label="Empenhado")
        ax.plot(indices, val_realizado,  marker='s', label="Realizado")

        ax.set_xticks(indices)
        ax.set_xticklabels(sorted_years)
        ax.set_ylabel("Valores (R$)")
        ax.set_title(f"{orgao} - {acao} - {categoria}")
        ax.legend()

        self.canvas.draw()

    # ---------------------------------------------
    # ABA 2: Exemplo de outra análise
    # ---------------------------------------------
    def setup_tab_secondary(self):
        """
        Configura a segunda aba, que pode conter outro tipo de análise ou gráfico.
        Neste exemplo, apenas colocamos um placeholder.
        """
        layout = QVBoxLayout(self.tab_secondary)
        label = QLabel("Em construção: espaço para outra análise ou gráfico")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    # ---------------------------------------------
    # ABA 3: Qualquer outro insight
    # ---------------------------------------------
    def setup_tab_third(self):
        """
        Configura a terceira aba, onde podem ser adicionados novos gráficos,
        tabelas ou estatísticas.
        """
        layout = QVBoxLayout(self.tab_third)
        label = QLabel("Outros insights podem ser exibidos aqui.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
