import os
import json
import pandas as pd
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QDialog, 
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt
from paths import CADASTRO_OBJETOS_AUDITAVEIS_PATH
from .tableview import RiscoDelegate, CustomTableView, ExcelModelManager, load_config
from utils.styles.style_add_button import apply_button_style
from utils.styles.style_table import apply_table_style
from .edit_dialog import EditDialog
from .add_dialog import AddAuditavelDialog, save_new_entry
from .relatorio_dialog import open_relatorio_dialog
from datetime import datetime
from utils.styles.style_add_button import add_button_func

def create_vigencia_contratos(title_text, icons):
    icons = icons
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    # Barra de título e botões
    title_layout = QHBoxLayout()
    title_label = QLabel(title_text)
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()

    def open_add_dialog_indep(parent):
        dialog = AddAuditavelDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_entry = dialog.get_data()
            save_new_entry(new_entry)
            load_model_from_json()

    def export_to_excel():
        from datetime import datetime
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices

        datahora = datetime.now().strftime("%d%m%Y_%H%M")
        default_filename = f"mapa_criterio_{datahora}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            main_frame,
            "Exportar para Excel",
            default_filename,
            "Arquivos Excel (*.xlsx)"
        )
        if not file_path:
            return

        config = load_config()
        if not config:
            QMessageBox.critical(main_frame, "Erro", "Configuração não encontrada.")
            return

        try:
            # Preparar dados da aba Compilado
            multiplicadores = config.get("multiplicador", {"materialidade": 4, "relevancia": 2, "criticidade": 4})
            objetos = config.get("objetos_auditaveis", [])
            compilado_data = []
            for obj in objetos:
                nr = obj.get("nr", "")
                descricao = obj.get("descricao", "")
                mat_raw = sum(v.get("valor", 0) for v in obj.get("materialidade", {}).values())
                rel_raw = sum(v.get("valor", 0) for v in obj.get("relevancia", {}).values())
                crit_raw = sum(v.get("valor", 0) for v in obj.get("criticidade", {}).values())
                mat_val = mat_raw * multiplicadores.get("materialidade", 4)
                rel_val = rel_raw * multiplicadores.get("relevancia", 2)
                crit_val = crit_raw * multiplicadores.get("criticidade", 4)
                total = mat_val + rel_val + crit_val

                risco = obj.get("risco", "")
                if not risco:
                    riscos = config.get("riscos", {"Muito Alto": 250, "Alto": 200, "Médio": 150, "Baixo": 100, "Muito Baixo": 50})
                    sorted_riscos = sorted(riscos.items(), key=lambda x: x[1], reverse=True)
                    for label, threshold in sorted_riscos:
                        if total >= threshold:
                            risco = label
                            break
                    else:
                        risco = sorted_riscos[-1][0]

                compilado_data.append({
                    "NR": nr,
                    "Objetos Auditáveis": descricao,
                    "Materialidade": mat_val,
                    "Relevância": rel_val,
                    "Criticidade": crit_val,
                    "Total": total,
                    "Risco": risco
                })
            df_compilado = pd.DataFrame(compilado_data)

            # Função auxiliar para construir DataFrame das abas de critérios
            def build_df(chave):
                dados = []
                for criterio in config.get("pontuacao_criterios", {}).get(chave, []):
                    for opcao in criterio.get("opcoes", []):
                        dados.append({
                            "Critério": criterio.get("Critério", ""),
                            "Tipo": criterio.get("Tipo", ""),
                            "Descrição": opcao.get("Descrição", ""),
                            "Pontuação": opcao.get("Pontuação", "")
                        })
                return pd.DataFrame(dados)

            df_materialidade = build_df("materialidade")
            df_relevancia = build_df("relevancia")
            df_criticidade = build_df("criticidade")

            # Gravação em arquivo Excel
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                df_compilado.to_excel(writer, sheet_name="Compilado", index=False)
                df_materialidade.to_excel(writer, sheet_name="Materialidade", index=False)
                df_relevancia.to_excel(writer, sheet_name="Relevância", index=False)
                df_criticidade.to_excel(writer, sheet_name="Criticidade", index=False)

            QMessageBox.information(main_frame, "Sucesso", "Exportação realizada com sucesso!")
            # Abre automaticamente o arquivo gerado
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(main_frame, "Erro", f"Falha ao exportar para Excel: {e}")

    def import_from_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            main_frame,
            "Importar do Excel",
            "",
            "Arquivos Excel (*.xlsx)"
        )
        if file_path:
            excel_manager = ExcelModelManager(file_path)
            if excel_manager.validate():
                df_objetos_auditaveis = pd.read_excel(file_path, sheet_name="Objetos Auditáveis", dtype=str).fillna("")

                objetos_auditaveis = []
                for _, row in df_objetos_auditaveis.iterrows():
                    nr = row["NR"]
                    tipo_de_servico = row["Tipo de Serviço"]
                    objeto_auditavel = row["Objetos Auditáveis"]
                    objetivo_auditoria = row["Objetivo da Auditoria"]
                    origem_demanda = row["Origem da Demanda"]

                    # Converte datas para o formato "YYYY-MM-DD"
                    inicio = row["Início"]
                    conclusao = row["Conclusão"]
                    if inicio:
                        try:
                            inicio = pd.to_datetime(inicio).strftime("%Y-%m-%d")
                        except Exception:
                            pass
                    if conclusao:
                        try:
                            conclusao = pd.to_datetime(conclusao).strftime("%Y-%m-%d")
                        except Exception:
                            pass

                    hh = row["HH"]
                    situacao = row["Situação"]
                    observacoes = row["Observações/Justificativas"]
                    objetos_auditaveis.append({
                        "nr": nr,
                        "tipo_de_servico": tipo_de_servico,
                        "descricao": objeto_auditavel,
                        "objetivo_auditoria": objetivo_auditoria,
                        "origem_demanda": origem_demanda,
                        "inicio": inicio,
                        "conclusao": conclusao,
                        "hh": hh,
                        "situacao": situacao,
                        "observacoes": observacoes
                    })

                # Cria o item pai "riscos" com os 5 níveis e seus thresholds
                config = {
                    "objetos_auditaveis": objetos_auditaveis,
                }

                try:
                    with open(CADASTRO_OBJETOS_AUDITAVEIS_PATH, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    QMessageBox.information(main_frame, "Sucesso", "Configuração salva com sucesso!")
                    load_model_from_json()
                except Exception as e:
                    QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar a configuração: {e}")
                                
    btn_export = add_button_func("Exportar", "export", export_to_excel, title_layout, icons, tooltip="Exportar dados")
    btn_import = add_button_func("Importar", "import", import_from_excel, title_layout, icons, tooltip="Importar dados")
    btn_adicionar = add_button_func("Adicionar", "add", open_add_dialog_indep, title_layout, icons, tooltip="Adicionar novo item")
    btn_relatorio = add_button_func("Relatório", "report", open_relatorio_dialog, title_layout, icons, tooltip="Visualizar relatório")

    main_layout.addLayout(title_layout)

    # Tabela principal (CustomTableView)
    table_view = CustomTableView()
    table_view.setFont(QFont("Arial", 12))  # Define fonte maior para melhor visibilidade


    apply_table_style(table_view)

    model = QStandardItemModel()
    table_view.setModel(model)
    headers = ["NR", "Tipo", "Objetos Auditáveis", "Objetivo da Auditoria", "Origem da Demanda", "Início", "Conclusão", "HH", "Situação", "Observações/Justificativas"]
    model.setHorizontalHeaderLabels(headers)
        
    # Centraliza os cabeçalhos da tabela principal
    for col in range(len(headers)):
        header_item = model.horizontalHeaderItem(col)
        if header_item:
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    table_view.verticalHeader().setDefaultSectionSize(30)


    main_layout.addWidget(table_view)

    def format_value(value):
        return str(int(value)) if value == int(value) else str(value)
    
    def load_model_from_json():
        config = load_config()
        model.clear()
        
        if not config:
            return
        
        model.setHorizontalHeaderLabels(headers)
        
        for item in config.get("objetos_auditaveis", []):
            nr = item.get("nr", "")
            tipo_de_servico = item.get("tipo_de_servico", "")
            descricao = item.get("descricao", "")
            objetivo_auditoria = item.get("objetivo_auditoria", "")
            origem_demanda = item.get("origem_demanda", "")
            inicio = item.get("inicio", "")
            conclusao = item.get("conclusao", "")
            hh = item.get("hh", "")
            situacao = item.get("situacao", "")
            observacoes = item.get("observacoes", "")
            
            # Converter datas de YYYY-MM-DD para DD/MM/YYYY
            if inicio:
                try:
                    inicio = datetime.strptime(inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    pass
            if conclusao:
                try:
                    conclusao = datetime.strptime(conclusao, '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    pass

            row = [
                QStandardItem(str(nr)),
                QStandardItem(str(tipo_de_servico)),
                QStandardItem(str(descricao)),
                QStandardItem(str(objetivo_auditoria)),
                QStandardItem(str(origem_demanda)),
                QStandardItem(str(inicio)),
                QStandardItem(str(conclusao)),
                QStandardItem(str(hh)),
                QStandardItem(str(situacao)),
                QStandardItem(str(observacoes))
            ]
            
            for cell in row:
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            model.appendRow(row)
        
        adjust_columns()

    def adjust_columns():
        table_view.setColumnWidth(0, 40)
        table_view.setColumnWidth(1, 100)
        table_view.setColumnWidth(4, 200)
        table_view.setColumnWidth(5, 100)
        table_view.setColumnWidth(6, 100)
        table_view.setColumnWidth(7, 70)
        table_view.setColumnWidth(8, 120)
        
        header = table_view.horizontalHeader()
        for col in range(model.columnCount()):
            if col == 2:  # Coluna que deve ocupar o espaço restante
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        
        # Esconde as colunas "Objetivo da Auditoria" e "Observações"
        table_view.hideColumn(3)
        table_view.hideColumn(9)


    load_model_from_json()

    def on_table_double_clicked(index):
        """Função chamada quando o usuário clica duas vezes em uma linha da tabela"""
        if not index.isValid():
            return
        
        row = index.row()
        
        # Carregar a configuração atual
        config = load_config()
        if not config:
            QMessageBox.critical(main_frame, "Erro", "Não foi possível carregar a configuração.")
            return
        
        # Obter o objeto auditável correspondente à linha clicada
        objetos_auditaveis = config.get("objetos_auditaveis", [])
        if row >= len(objetos_auditaveis):
            QMessageBox.critical(main_frame, "Erro", "Índice de linha inválido.")
            return
        
        objeto_auditavel = objetos_auditaveis[row]
        
        # Criar e exibir o diálogo de edição
        dialog = EditDialog(main_frame, objeto_auditavel, config, row)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Se o objeto foi excluído, não atualizamos o registro.
            if not dialog.deleted:
                updated_data = dialog.get_updated_data()
                config["objetos_auditaveis"][row] = updated_data
                try:
                    with open(CADASTRO_OBJETOS_AUDITAVEIS_PATH, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    QMessageBox.critical(main_frame, "Erro", f"Falha ao salvar a configuração: {e}")
            load_model_from_json()  # Atualiza o modelo da tabela

    
    # Conectar o evento de duplo clique na tabela
    table_view.doubleClicked.connect(on_table_double_clicked)
    btn_adicionar.clicked.connect(lambda: open_add_dialog_indep(main_frame))
    btn_import.clicked.connect(import_from_excel)
    btn_export.clicked.connect(export_to_excel)
    btn_relatorio.clicked.connect(lambda: open_relatorio_dialog(main_frame, model, headers))

    return main_frame