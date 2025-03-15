import requests
import webbrowser
import re
import pandas as pd
from PyQt6.QtWidgets import (
    QTableView, QMessageBox, QStyledItemDelegate,
)
from PyQt6.QtGui import QStandardItem, QBrush, QColor
from database.db_manager import DatabaseManager
from paths import CCIMAR12_PATH
from datetime import datetime
from PyQt6.QtCore import Qt
from pathlib import Path
import tempfile
import subprocess

def create_tables():
    db = DatabaseManager(CCIMAR12_PATH)
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS atas_unidades (
            id_unidade INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_unidade TEXT UNIQUE NOT NULL,
            nome_unidade TEXT NOT NULL
        );
    """)
    
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS atas_detalhes (
            id_ata INTEGER PRIMARY KEY AUTOINCREMENT,
            id_unidade INTEGER NOT NULL,
            numeroControlePNCPAta TEXT,
            numeroAtaRegistroPreco TEXT,
            anoAta INTEGER,
            numeroControlePNCPCompra TEXT,
            cancelado BOOLEAN,
            dataCancelamento TEXT,
            dataAssinatura TEXT,
            vigenciaInicio TEXT,
            vigenciaFim TEXT,
            dataPublicacaoPncp TEXT,
            dataInclusao TEXT,
            dataAtualizacao TEXT,
            dataAtualizacaoGlobal TEXT,
            usuario TEXT,
            objetoContratacao TEXT,
            cnpjOrgao TEXT,
            nomeOrgao TEXT,
            FOREIGN KEY (id_unidade) REFERENCES atas_unidades(id_unidade) ON DELETE CASCADE
        );
    """)
    print("Tabelas criadas com sucesso!")

### 📌 CONSULTA À API ###
def consultar_atas(data_inicial, data_final, cnpj, codigo_unidade):
    pagina = 1
    tamanho_pagina = 500
    all_data = []

    while True:
        url = f"https://pncp.gov.br/api/consulta/v1/atas?dataInicial={data_inicial}&dataFinal={data_final}&cnpj={cnpj}&codigoUnidadeAdministrativa={codigo_unidade}&pagina={pagina}&tamanhoPagina={tamanho_pagina}"
        print(f"Consultando página {pagina}...") 

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                all_data.extend(data["data"])  
                print(f"Página {pagina} carregada com {len(data['data'])} registros.")  
            else:
                print(f"Página {pagina} vazia ou sem dados.")  
                break  

            total_paginas = data.get("totalPaginas", 1)
            if pagina >= total_paginas:
                print(f"Todas as {total_paginas} páginas foram consultadas.")  
                break  

            pagina += 1  

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(None, "Error", f"API request failed: {e}")
            return None

    return all_data

### 📌 SALVANDO OS DADOS NO BANCO DE DADOS ###
def save_atas_to_db(atas):
    db = DatabaseManager(CCIMAR12_PATH)
    for item in atas:
        # Verifica se a unidade já existe
        unidade = db.execute_query("SELECT id_unidade FROM atas_unidades WHERE codigo_unidade = ?", 
                                   (item["codigoUnidadeOrgao"],))
        if unidade:
            id_unidade = unidade[0][0]
        else:
            db.execute_update(
                "INSERT INTO atas_unidades (codigo_unidade, nome_unidade) VALUES (?, ?)",
                (item["codigoUnidadeOrgao"], item["nomeUnidadeOrgao"])
            )
            id_unidade = db.execute_query("SELECT last_insert_rowid()")[0][0]

        # Verifica se a ata já existe na tabela
        ata_existente = db.execute_query("SELECT id_ata FROM atas_detalhes WHERE numeroControlePNCPAta = ?", 
                                         (item["numeroControlePNCPAta"],))

        if ata_existente:
            # Se existir, atualiza os dados
            db.execute_update("""
                UPDATE atas_detalhes 
                SET id_unidade=?, numeroAtaRegistroPreco=?, anoAta=?, numeroControlePNCPCompra=?, cancelado=?,
                    dataCancelamento=?, dataAssinatura=?, vigenciaInicio=?, vigenciaFim=?, dataPublicacaoPncp=?,
                    dataInclusao=?, dataAtualizacao=?, dataAtualizacaoGlobal=?, usuario=?, objetoContratacao=?,
                    cnpjOrgao=?, nomeOrgao=?
                WHERE numeroControlePNCPAta=?
            """, (
                id_unidade, item["numeroAtaRegistroPreco"], item["anoAta"],
                item["numeroControlePNCPCompra"], item["cancelado"], item["dataCancelamento"],
                item["dataAssinatura"], item["vigenciaInicio"], item["vigenciaFim"],
                item["dataPublicacaoPncp"], item["dataInclusao"], item["dataAtualizacao"],
                item["dataAtualizacaoGlobal"], item["usuario"], item["objetoContratacao"],
                item["cnpjOrgao"], item["nomeOrgao"], item["numeroControlePNCPAta"]
            ))
            print(f"🔄 Atualizado: {item['numeroControlePNCPAta']}")
        
        else:
            # Se não existir, insere um novo registro
            db.execute_update("""
                INSERT INTO atas_detalhes (
                    id_unidade, numeroControlePNCPAta, numeroAtaRegistroPreco, anoAta, numeroControlePNCPCompra, cancelado,
                    dataCancelamento, dataAssinatura, vigenciaInicio, vigenciaFim, dataPublicacaoPncp,
                    dataInclusao, dataAtualizacao, dataAtualizacaoGlobal, usuario, objetoContratacao,
                    cnpjOrgao, nomeOrgao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_unidade, item["numeroControlePNCPAta"], item["numeroAtaRegistroPreco"], item["anoAta"],
                item["numeroControlePNCPCompra"], item["cancelado"], item["dataCancelamento"],
                item["dataAssinatura"], item["vigenciaInicio"], item["vigenciaFim"],
                item["dataPublicacaoPncp"], item["dataInclusao"], item["dataAtualizacao"],
                item["dataAtualizacaoGlobal"], item["usuario"], item["objetoContratacao"],
                item["cnpjOrgao"], item["nomeOrgao"]
            ))
            print(f"✅ Inserido: {item['numeroControlePNCPAta']}")

    print("🔄 Dados processados com sucesso!")


### 📌 CARREGAMENTO NO TREEVIEW ###
def load_unidades(model):
    """Carrega unidades no TreeView, garantindo que a tabela atas_unidades exista."""
    db = DatabaseManager(CCIMAR12_PATH)

    # Verifica se a tabela existe antes de consultar
    tabela_existe = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='atas_unidades';")
    if not tabela_existe:
        print("⚠️ A tabela atas_unidades não existe. Criando agora...")
        create_tables()  # Criar tabelas se não existirem
        return  # Não tenta carregar dados agora, pois a tabela acabou de ser criada

    unidades = db.execute_query("SELECT id_unidade, codigo_unidade, nome_unidade FROM atas_unidades")

    if unidades is None:
        print("⚠️ Nenhum dado encontrado na tabela atas_unidades.")
        return  # Evita erro ao tentar iterar sobre None

    for unidade in unidades:
        id_unidade, codigo, nome = unidade
        parent_item = QStandardItem(f"{codigo} - {nome}")
        parent_item.setData(id_unidade)
        parent_item.setChild(0, QStandardItem("Carregando..."))  # Placeholder
        model.appendRow([parent_item])

    print(f"✅ {len(unidades)} unidades carregadas com sucesso.")

def extract_pncp_values(numeroControlePNCPAta):
    """
    Usa regex para extrair CNPJ, ano, sequencial da compra e número da ata.
    Exemplo correto: 00394502000144-1-002900/2024-000019
    """
    # print(f"🔍 [DEBUG] Analisando numeroControlePNCPAta: '{numeroControlePNCPAta}'")  # Depuração antes da regex

    # Regex ajustado para corresponder ao formato correto
    pattern = r"^(\d{14})-\d{1}-(\d{6})/(\d{4})-(\d{6})$"
    match = re.match(pattern, numeroControlePNCPAta)

    if match:
        cnpj, sequencialcompra, ano, numeroAta = match.groups()
        # print(f"✅ [DEBUG] Regex Correspondência Encontrada: CNPJ={cnpj}, SeqCompra={sequencialcompra}, Ano={ano}, NumAta={numeroAta}")  # Log de sucesso
        return cnpj, sequencialcompra, ano, numeroAta

    # print("❌ [ERRO] Não foi possível extrair os dados do númeroControlePNCPAta.")  # Log de erro
    return None, None, None, None

def fetch_pdf_link(numeroControlePNCPAta):
    """
    Faz a requisição para obter a URL do arquivo PDF com base no numeroControlePNCPAta.
    """
    cnpj, sequencialcompra, ano, numeroAta = extract_pncp_values(numeroControlePNCPAta)

    if not cnpj or not sequencialcompra or not ano or not numeroAta:
        print("❌ [ERRO] Dados extraídos inválidos.")
        return None

    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencialcompra}/atas/{numeroAta}/arquivos?pagina=1&tamanhoPagina=500"
    # print(f"🔗 [DEBUG] Consultando API para PDF: {url}")  # Log

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # print(f"📥 [DEBUG] Resposta da API: {data}")  # Exibe toda a resposta para depuração

        if data and isinstance(data, list) and "url" in data[0]:
            # print(f"✅ [DEBUG] Documento encontrado: {data[0]['url']}")  # Log de sucesso
            return data[0]["url"]
        else:
            # print("❌ [ERRO] Nenhum documento encontrado na API.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ [ERRO] Erro na requisição: {e}")
        return None
    
def format_date(date_str):
    """Converte data de 'YYYY-MM-DD' para 'DD/MM/YYYY'."""
    if date_str and isinstance(date_str, str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return date_str  
    return "N/A"  
            
def load_atas_detalhes(model, parent_item, icons):
    """Carrega detalhes das atas ao expandir uma unidade no TreeView e adiciona um hiperlink ao PDF."""
    id_unidade = parent_item.data()

    db = DatabaseManager(CCIMAR12_PATH)
    atas = db.execute_query("""
        SELECT numeroControlePNCPAta, numeroAtaRegistroPreco, anoAta, numeroControlePNCPCompra, cancelado,
               dataCancelamento, dataAssinatura, vigenciaInicio, vigenciaFim, dataPublicacaoPncp,
               dataInclusao, dataAtualizacao, dataAtualizacaoGlobal, usuario, objetoContratacao,
               cnpjOrgao, nomeOrgao
        FROM atas_detalhes WHERE id_unidade = ?
    """, (id_unidade,))

    if atas:
        parent_item.removeRow(0)  # Remove o placeholder "Carregando..."
        for ata in atas:
            (numeroControlePNCPAta, numeroAta, ano, numeroControlePNCPCompra, cancelado,
             dataCancelamento, dataAssinatura, vigenciaInicio, vigenciaFim, dataPublicacaoPncp,
             dataInclusao, dataAtualizacao, dataAtualizacaoGlobal, usuario, objetoContratacao,
             cnpjOrgao, nomeOrgao) = ata

            # Converter as datas para DD/MM/YYYY
            inicio_formatado = format_date(vigenciaInicio)
            fim_formatado = format_date(vigenciaFim)

            # Criar item principal com texto formatado
            ata_item = QStandardItem(f"Ata {numeroAta}/{ano} - Vigência: {inicio_formatado} a {fim_formatado}")

            # Criar item "Detalhes da Ata" como filho
            detalhes_item = QStandardItem("📄 Detalhes da Ata")
            detalhes = [
                f"🔢 Número de Controle: {numeroControlePNCPAta}",
                f"🆔 Número da Compra: {numeroControlePNCPCompra}",
                f"📌 Cancelado: {'Sim' if cancelado else 'Não'}",
                f"📅 Data Cancelamento: {format_date(dataCancelamento)}",
                f"📅 Data Assinatura: {format_date(dataAssinatura)}",
                f"📅 Publicação PNCP: {format_date(dataPublicacaoPncp)}",
                f"📅 Inclusão: {format_date(dataInclusao)}",
                f"📅 Atualização: {format_date(dataAtualizacao)}",
                f"👤 Usuário: {usuario}",
                f"📝 Objeto: {objetoContratacao}",
                f"🏢 CNPJ Órgão: {cnpjOrgao}",
                f"🏢 Nome Órgão: {nomeOrgao}",
            ]

            for detalhe in detalhes:
                detalhes_item.appendRow(QStandardItem(detalhe))

            # 🔗 Criar item do link para o PDF
            pdf_url = fetch_pdf_link(numeroControlePNCPAta)
            if pdf_url:
                pdf_link_item = QStandardItem("🔗 Documento PDF (Clique para abrir)")
                pdf_link_item.setData(pdf_url, Qt.ItemDataRole.UserRole)  # Armazena a URL do PDF
                pdf_link_item.setToolTip("Clique para abrir o documento PDF")  # Tooltip
                pdf_link_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Habilita seleção e clique
                pdf_link_item.setForeground(QBrush(QColor(0, 0, 255)))  # Define a cor azul para parecer um hiperlink

                # Adiciona o link como filho dos detalhes
                detalhes_item.appendRow(pdf_link_item)

            # Adicionar os detalhes como filho da ata
            ata_item.appendRow([detalhes_item])
            parent_item.appendRow([ata_item])