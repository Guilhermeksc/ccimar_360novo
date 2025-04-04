import json
from pathlib import Path

def filtrar_dados(json_data):
    return {
        "valorTotalEstimado": json_data.get("valorTotalEstimado"),
        "valorTotalHomologado": json_data.get("valorTotalHomologado"),
        "orcamentoSigilosoCodigo": json_data.get("orcamentoSigilosoCodigo"),
        "orcamentoSigilosoDescricao": json_data.get("orcamentoSigilosoDescricao"),
        "numeroControlePNCP": json_data.get("numeroControlePNCP"),
        "linkSistemaOrigem": json_data.get("linkSistemaOrigem"),
        "linkProcessoEletronico": json_data.get("linkProcessoEletronico"),
        "anoCompra": json_data.get("anoCompra"),
        "sequencialCompra": json_data.get("sequencialCompra"),
        "numeroCompra": json_data.get("numeroCompra"),
        "processo": json_data.get("processo"),
        "ufNome": json_data.get("unidadeOrgao", {}).get("ufNome"),
        "ufSigla": json_data.get("unidadeOrgao", {}).get("ufSigla"),
        "municipioNome": json_data.get("unidadeOrgao", {}).get("municipioNome"),
        "codigoUnidade": json_data.get("unidadeOrgao", {}).get("codigoUnidade"),
        "nomeUnidade": json_data.get("unidadeOrgao", {}).get("nomeUnidade"),
        "modalidadeId": json_data.get("modalidadeId"),
        "modalidadeNome": json_data.get("modalidadeNome"),
        "justificativaPresencial": json_data.get("justificativaPresencial"),
        "modoDisputaId": json_data.get("modoDisputaId"),
        "modoDisputaNome": json_data.get("modoDisputaNome"),
        "tipoInstrumentoConvocatorioCodigo": json_data.get("tipoInstrumentoConvocatorioCodigo"),
        "tipoInstrumentoConvocatorioNome": json_data.get("tipoInstrumentoConvocatorioNome"),
        "amparoLegal": {
            "codigo": json_data.get("amparoLegal", {}).get("codigo"),
            "descricao": json_data.get("amparoLegal", {}).get("descricao"),
            "nome": json_data.get("amparoLegal", {}).get("nome")
        },
        "objetoCompra": json_data.get("objetoCompra"),
        "informacaoComplementar": json_data.get("informacaoComplementar"),
        "srp": json_data.get("srp"),
        "dataPublicacaoPncp": json_data.get("dataPublicacaoPncp"),
        "dataAberturaProposta": json_data.get("dataAberturaProposta"),
        "dataEncerramentoProposta": json_data.get("dataEncerramentoProposta"),
        "situacaoCompraId": json_data.get("situacaoCompraId"),
        "situacaoCompraNome": json_data.get("situacaoCompraNome"),
        "existeResultado": json_data.get("existeResultado"),
        "dataInclusao": json_data.get("dataInclusao"),
        "dataAtualizacao": json_data.get("dataAtualizacao"),
        "dataAtualizacaoGlobal": json_data.get("dataAtualizacaoGlobal")
    }

def agrupar_jsons(ano: int, cnpj: str):
    pasta = Path.cwd() / str(ano)
    arquivos = list(pasta.glob(f"Ano{ano}Sequencial_*_{cnpj}.json"))
    arquivos = [f for f in arquivos if "_404" not in f.name]

    dados_filtrados = []

    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
            for item in conteudo.values():
                dados_filtrados.append(filtrar_dados(item))

    arquivo_saida = pasta / f"Ano{ano}_consolidado_{cnpj}.json"
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(dados_filtrados, f, ensure_ascii=False, indent=2)

# Exemplo de uso:
agrupar_jsons(ano=2025, cnpj="00394502000144")
