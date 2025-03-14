import os
import json
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QRadioButton, QLineEdit, QHBoxLayout, QVBoxLayout,
    QPushButton, QDialogButtonBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from paths import CADASTRO_OBJETOS_AUDITAVEIS_PATH

def open_relatorio_dialog(parent, model, headers):
    dialog = RelatorioDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        option = dialog.get_selected_option()
        folder = dialog.folder_edit.text().strip()
        if not folder:
            QMessageBox.warning(parent, "Atenção", "Local de salvamento não definido.")
            return
        if option == "servicos":
            export_servicos_auditoria(folder, model, headers, parent)
        elif option == "resumido":
            QMessageBox.information(parent, "Info", "Relatório Resumido não implementado.")
        elif option == "homem_hora":
            QMessageBox.information(parent, "Info", "Relatório Homem-hora não implementado.")

# Classe de diálogo para seleção das opções de relatório
class RelatorioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Gerar Relatório")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # Opções via RadioButtons
        self.radio_servicos = QRadioButton("Serviços de Auditoria")
        self.radio_resumido = QRadioButton("Relatório Resumido")
        self.radio_homem_hora = QRadioButton("Relatório Homem-hora")
        self.radio_servicos.setChecked(True)
        layout.addWidget(self.radio_servicos)
        layout.addWidget(self.radio_resumido)
        layout.addWidget(self.radio_homem_hora)
        
        # Seleção do local de salvamento
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Definir local de salvamento")
        btn_select = QPushButton("Selecionar")
        btn_select.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(btn_select)
        layout.addLayout(folder_layout)
        
        # Botões OK/Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione o local de salvamento")
        if folder:
            self.folder_edit.setText(folder)
    
    def get_selected_option(self):
        if self.radio_servicos.isChecked():
            return "servicos"
        elif self.radio_resumido.isChecked():
            return "resumido"
        elif self.radio_homem_hora.isChecked():
            return "homem_hora"
        return None

# Função para exportar "Serviços de Auditoria"
def export_servicos_auditoria(folder, model, headers, main_frame):
    import os
    import pandas as pd
    from datetime import datetime
    from PyQt6.QtWidgets import QMessageBox

    # Cria a estrutura de pastas: folder/PAINT/Objetos Auditáveis
    paint_dir = os.path.join(folder, "PAINT")
    objetos_dir = os.path.join(paint_dir, "Objetos Auditáveis")
    os.makedirs(objetos_dir, exist_ok=True)

    datahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"servicos_auditoria_{datahora}.xlsx"
    file_path = os.path.join(objetos_dir, file_name)

    # Extrai os dados do model para um DataFrame
    num_rows = model.rowCount()
    data = []
    for row in range(num_rows):
        row_data = []
        for col in range(model.columnCount()):
            item = model.item(row, col)
            row_data.append(item.text() if item else "")
        data.append(row_data)

    df = pd.DataFrame(data, columns=headers)

    # Caso queira que a coluna HH seja numérica para a soma:
    try:
        df[headers[7]] = pd.to_numeric(df[headers[7]], errors='coerce')
    except:
        pass

    # Usaremos xlsxwriter para formatação detalhada
    try:
        import xlsxwriter

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            # Cria a planilha manualmente para ter controle sobre formatação
            workbook = writer.book
            worksheet = workbook.add_worksheet("Compilado")
            writer.sheets["Compilado"] = worksheet
            worksheet.set_row(0, 30)  # Linha 1
            worksheet.set_row(1, 30)  # Linha 2            

            # ---------------------------
            # 1) Definição de formatos
            # ---------------------------
            title_format = workbook.add_format({
                'text_wrap': True,
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter'
            })

            header_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': '#CCCCCC'
            })

            # Linhas pares (fundo branco)
            even_row_format = workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': '#FFFFFF'
            })

            # Linhas ímpares (fundo cinza claro)
            odd_row_format = workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': '#F9F9F9'
            })

            # Formato para a célula "Total de HH"
            sum_title_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': '#D9D9D9'
            })

            # Formato para a célula do valor somado
            sum_value_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'valign': 'vcenter'
            })

            # ---------------------------
            # 2) Título mesclado (duas linhas)
            # ---------------------------
            # Vamos usar as duas primeiras linhas (0 e 1) para o título
            title_text = "PAINT-2026\nServiços de Auditoria"
            worksheet.merge_range(0, 0, 1, len(headers) - 1, title_text, title_format)

            # ---------------------------
            # 3) Cabeçalho na linha 2
            # ---------------------------
            for col_num, col_name in enumerate(headers):
                worksheet.write(2, col_num, col_name, header_format)

            # ---------------------------
            # 4) Dados da tabela (linhas zebradas)
            # ---------------------------
            start_data_row = 3  # dados a partir da linha 3 (0-based no xlsxwriter)
            for i in range(df.shape[0]):
                # Alterna a cor de fundo entre par/ímpar
                row_format = even_row_format if i % 2 == 0 else odd_row_format
                for col_num in range(df.shape[1]):
                    worksheet.write(start_data_row + i, col_num, df.iloc[i, col_num], row_format)

            # ---------------------------
            # 5) Linha de soma de HH
            # ---------------------------
            # A linha de soma fica logo após o último registro
            sum_row = start_data_row + df.shape[0]
            # Mescla colunas 5 (F) e 6 (G) para exibir "Total de HH"
            worksheet.merge_range(sum_row, 5, sum_row, 6, "Total de HH", sum_title_format)

            # Fórmula SOMA para coluna 7 (H em Excel),
            # lembrando que, em Excel, as linhas começam em 1.
            # Se start_data_row=3, a primeira linha de dados em Excel é linha 4.
            first_data_row_excel = start_data_row + 1
            last_data_row_excel = start_data_row + df.shape[0]
            # Ex: =SOMA(H4:H10)
            worksheet.write_formula(
                sum_row,
                7,
                f"=SOMA(H{first_data_row_excel}:H{last_data_row_excel})",
                sum_value_format
            )
            # Criação de um formato centralizado
            center_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter'
            })

            # Considerando que a linha imediatamente após (sum_row + 1) ficará em branco:
            # Segunda linha após: "Guilherme" na coluna E (índice 4)
            worksheet.write(sum_row + 2, 4, "Guilherme", center_format)
            # Terceira linha após: "Capitão de Corveta (IM)" na coluna E
            worksheet.write(sum_row + 3, 4, "Capitão de Corveta (IM)", center_format)
            # Quarta linha após: "Encarregado da divisão de planejamento" na coluna E
            worksheet.write(sum_row + 4, 4, "Encarregado da divisão de planejamento", center_format)
            # Quinta linha após: Na coluna E (índice 4), insere "ASSINADO DIGITALMENTE" com borda simples e centralizado
            sign_format = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            worksheet.write(sum_row + 5, 4, "ASSINADO DIGITALMENTE", sign_format)
            # ---------------------------
            # Exemplo de larguras (ajuste conforme necessário)
            col_widths = [4, 13, 20, 40, 22, 10, 10, 7, 10, 30]
            for col_idx, width in enumerate(col_widths):
                worksheet.set_column(col_idx, col_idx, width)

            # Ajuste para paisagem e "cabendo em 1 página de largura"
            worksheet.set_landscape()
            worksheet.fit_to_pages(1, 0)  # 1 página de largura, altura ilimitada

        QMessageBox.information(main_frame, "Sucesso", f"Arquivo exportado:\n{file_path}")
    except Exception as e:
        QMessageBox.critical(main_frame, "Erro", f"Erro ao exportar:\n{e}")
