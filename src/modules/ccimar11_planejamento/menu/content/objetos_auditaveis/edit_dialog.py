from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QDialog, 
    QComboBox, QFormLayout, QTabWidget, QDialogButtonBox,
    QWidget
)
from PyQt6.QtCore import Qt
from utils.styles.styles_edit_button import apply_edit_dialog_style
        
class EditDialog(QDialog):
    def __init__(self, parent=None, objeto_auditavel=None, config=None, row_index=None):
        super().__init__(parent)
        self.objeto_auditavel = objeto_auditavel
        self.config = config
        self.row_index = row_index
        self.pontuacao_criterios = config.get("pontuacao_criterios", {})
        self.comboboxes = {}
        
        self.setWindowTitle(f"Editar Objeto Auditável: {objeto_auditavel.get('descricao', '')}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Estilo para o diálogo
        apply_edit_dialog_style(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Informações básicas
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #2D2D44; border-radius: 5px; padding: 10px;")
        info_layout = QHBoxLayout(info_frame)
        
        nr_label = QLabel(f"<b>NR:</b> {objeto_auditavel.get('nr', '')}")
        nr_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(nr_label)
        
        desc_label = QLabel(f"<b>Descrição:</b> {objeto_auditavel.get('descricao', '')}")
        desc_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(desc_label)
        
        main_layout.addWidget(info_frame)
        
        # Criar abas para cada categoria
        tab_widget = QTabWidget()
        
        # Aba de Materialidade
        materialidade_tab = QWidget()
        materialidade_layout = QFormLayout(materialidade_tab)
        materialidade_layout.setContentsMargins(15, 15, 15, 15)
        materialidade_layout.setSpacing(10)
        self.setup_category_tab(materialidade_layout, "materialidade")
        tab_widget.addTab(materialidade_tab, "Materialidade")
        
        # Aba de Relevância
        relevancia_tab = QWidget()
        relevancia_layout = QFormLayout(relevancia_tab)
        relevancia_layout.setContentsMargins(15, 15, 15, 15)
        relevancia_layout.setSpacing(10)
        self.setup_category_tab(relevancia_layout, "relevancia")
        tab_widget.addTab(relevancia_tab, "Relevância")
        
        # Aba de Criticidade
        criticidade_tab = QWidget()
        criticidade_layout = QFormLayout(criticidade_tab)
        criticidade_layout.setContentsMargins(15, 15, 15, 15)
        criticidade_layout.setSpacing(10)
        self.setup_category_tab(criticidade_layout, "criticidade")
        tab_widget.addTab(criticidade_tab, "Criticidade")
        
        main_layout.addWidget(tab_widget)
        
        # Botões de OK e Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Estilizar os botões
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Salvar")
        ok_button.setMinimumWidth(100)
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancelar")
        cancel_button.setStyleSheet("background-color: #f44336;")
        cancel_button.setMinimumWidth(100)
        
        main_layout.addWidget(button_box, 0, Qt.AlignmentFlag.AlignRight)
    
    def setup_category_tab(self, layout, category):
        """Configura os comboboxes para uma categoria específica (materialidade, relevância, criticidade)"""
        criterios = self.pontuacao_criterios.get(category, [])
        objeto_category = self.objeto_auditavel.get(category, {})
        
        for criterio_info in criterios:
            criterio_nome = criterio_info.get("Critério", "")
            opcoes = criterio_info.get("opcoes", [])
            
            # Criar combobox
            combo = QComboBox()
            combo.setMinimumWidth(450)
            combo.setMinimumHeight(30)
            
            # Adicionar opções ao combobox
            selected_index = 0
            for idx, opcao in enumerate(opcoes):
                desc = opcao.get("Descrição", "")
                pont = opcao.get("Pontuação", 0)
                display_text = f"{desc} ({pont} pts)"
                combo.addItem(display_text, opcao)
                
                # Verificar se esta é a opção atualmente selecionada
                criterio_atual = objeto_category.get(criterio_nome, {})
                if criterio_atual.get("texto", "") == desc:
                    selected_index = idx
            
            # Definir o índice selecionado
            combo.setCurrentIndex(selected_index)
            
            # Armazenar referência ao combobox
            self.comboboxes[(category, criterio_nome)] = combo
            
            # Criar label com estilo
            label = QLabel(f"{criterio_nome}:")
            label.setStyleSheet("font-weight: bold; font-size: 13px;")
            
            # Adicionar ao layout
            layout.addRow(label, combo)
    
    def get_updated_data(self):
        """Retorna os dados atualizados com base nas seleções do usuário"""
        updated_objeto = self.objeto_auditavel.copy()
        
        for (category, criterio_nome), combo in self.comboboxes.items():
            selected_index = combo.currentIndex()
            if selected_index >= 0:
                selected_option = combo.itemData(selected_index)
                desc = selected_option.get("Descrição", "")
                pont = selected_option.get("Pontuação", 0)
                
                # Atualizar o objeto auditável
                if category in updated_objeto:
                    if criterio_nome in updated_objeto[category]:
                        updated_objeto[category][criterio_nome] = {
                            "valor": pont,
                            "texto": desc
                        }
        
        return updated_objeto
