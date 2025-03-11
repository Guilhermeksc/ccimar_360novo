# paths/__init__.py

# Importando diretamente os objetos ou funções de cada módulo interno
from .base_path import *
from .config_path import *
from modules.ccimar10_auditoria import CCIMAR10_DIR, CCIMAR10_PATH
from modules.ccimar11_planejamento import (
    CCIMAR11_DIR, CCIMAR11_PATH, ACOES_ORCAMENTARIAS_SQL_PATH, TEMPLATE_TEST1_PATH, 
    TEMPLATE_TEST2_PATH, TEMPLATE_TEST3_PATH, TEMPLATE_RELATORIO_PATH, OBJETIVOS_NAVAIS_PATH, 
    OM_REPRESENTATIVAS_PATH, CONFIG_PAINT_PATH, CADASTRO_OBJETOS_AUDITAVEIS_PATH
)
from modules.ccimar12_licitacao import CCIMAR12_DIR, CCIMAR12_PATH
from modules.ccimar13_execucao import CCIMAR13_DIR, CCIMAR13_PATH, CARTAO_CORPORATIVO_PATH
from modules.ccimar14_pagamento import CCIMAR14_DIR, CCIMAR14_PATH
from modules.ccimar15_material import CCIMAR15_DIR, CCIMAR15_PATH
from modules.ccimar16_data_science import CCIMAR16_DIR, CCIMAR16_PATH, TEMPLATE_TEST_PATH
from modules.ccimar_utils import CCIMAR_UTIL_DIR, CCIMAR_UTIL_PATH


# Definindo __all__ para controle explícito do que será exportado
__all__ = [
    # base_path
    "BASE_DIR", "CONFIG_FILE", "ACOES_ORCAMENTARIAS_SQL_PATH", "DEFAULT_DATABASE_DIR", 
    "MODULES_DIR", "DEFAULT_JSON_DIR", "SQL_DIR", 
    "ASSETS_DIR", "TEMPLATE_DIR", "STYLE_PATH", "ICONS_DIR", "ICONS_MENU_DIR",
        
    # ccimar10_auditoria
    "CCIMAR10_DIR", "CCIMAR10_PATH",

    # ccimar11_planejamento
    "CCIMAR11_DIR", "CCIMAR11_PATH", "TEMPLATE_TEST1_PATH", "TEMPLATE_TEST2_PATH", 
    "TEMPLATE_TEST3_PATH", "TEMPLATE_RELATORIO_PATH", "OBJETIVOS_NAVAIS_PATH", 
    "OM_REPRESENTATIVAS_PATH", "CONFIG_PAINT_PATH", "CADASTRO_OBJETOS_AUDITAVEIS_PATH",

    # ccimar12_licitacao
    "CCIMAR12_DIR", "CCIMAR12_PATH",        

    # ccimar13_execução
    "CCIMAR13_DIR", "CCIMAR13_PATH", "CARTAO_CORPORATIVO_PATH",

    # ccimar14_pagamento
    "CCIMAR14_DIR", "CCIMAR14_PATH",

    # ccimar15_material
    "CCIMAR15_DIR", "CCIMAR15_PATH",        

    # ccimar16_data_science
    "CCIMAR16_DIR", "CCIMAR16_PATH", "TEMPLATE_TEST_PATH",

    # ccimar_utils
    "CCIMAR_UTIL_DIR", "CCIMAR_UTIL_PATH",

    # config_path
    "AGENTES_RESPONSAVEIS_FILE",
    ]
