# modules/widgets.py

# Utilidades
from utils.icon_loader import load_icons

from modules.ccimar_init.view import InicioWidget

from modules.ccimar10_auditoria.view import CCIMAR10View
from modules.ccimar10_auditoria.model import CCIMAR10Model
from modules.ccimar10_auditoria.controller import CCIMAR10Controller

from modules.ccimar11_planejamento.view import CCIMAR11View
from modules.ccimar11_planejamento.model import CCIMAR11Model
from modules.ccimar11_planejamento.controller import CCIMAR11Controller

from modules.ccimar12_licitacao.view import CCIMAR12View
from modules.ccimar12_licitacao.model import CCIMAR12Model
from modules.ccimar12_licitacao.controller import CCIMAR12Controller

from modules.ccimar13_execucao.view import CCIMAR13View
from modules.ccimar13_execucao.model import CCIMAR13Model
from modules.ccimar13_execucao.controller import CCIMAR13Controller

from modules.ccimar14_pagamento.view import CCIMAR14View
from modules.ccimar14_pagamento.model import CCIMAR14Model
from modules.ccimar14_pagamento.controller import CCIMAR14Controller

from modules.ccimar15_material.controller import CCIMAR15Controller
from modules.ccimar15_material.model import CCIMAR15Model
from modules.ccimar15_material.view import CCIMAR15View

from modules.ccimar16_data_science.view import CCIMAR16View
from modules.ccimar16_data_science.model import CCIMAR16Model
from modules.ccimar16_data_science.controller import CCIMAR16Controller

from modules.ccimar_utils.view import UtilsView
from modules.ccimar_utils.model import UtilsModel
from modules.ccimar_utils.controller import UtilsController


__all__ = [
    "InicioWidget",

    "CCIMAR10View",
    "CCIMAR10Model",
    "CCIMAR10Controller",

    "CCIMAR11View",
    "CCIMAR11Model",
    "CCIMAR11Controller",

    "CCIMAR12View",
    "CCIMAR12Model",
    "CCIMAR12Controller",

    "CCIMAR13View",
    "CCIMAR13Model",
    "CCIMAR13Controller",

    "CCIMAR14View",
    "CCIMAR14Model",
    "CCIMAR14Controller",

    "CCIMAR15View",
    "CCIMAR15Model",
    "CCIMAR15Controller",
    
    "CCIMAR16View",
    "CCIMAR16Model",
    "CCIMAR16Controller",
    
    "UtilsView",
    "UtilsModel",
    "UtilsController",
        
    # Utils
    "load_icons"
    ]