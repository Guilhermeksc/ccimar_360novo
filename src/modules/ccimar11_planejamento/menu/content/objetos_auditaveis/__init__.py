"""
Pacote objetos_auditaveis.

Este pacote contém os módulos relacionados à gestão de objetos auditáveis,
incluindo modelos, diálogos, persistência, cálculos e interface do usuário.
"""

from .dialogs import DetalhesDialog, CriteriosViewDialog
from .persistence import (
    load_multiplicadores, save_multiplicadores,
    load_objetos_criterios, save_objetos_criterios,
    update_objeto_criterios, get_objeto_criterios
)
from .calculations import (
    MultiplicadoresDialog
)
from .tableview import CustomTableView, ExcelModelManager, load_config
from .ui import create_objetos_auditaveis

__all__ = [
    'MultipicadoresDialog',
    'DetalhesDialog',
    'CriteriosViewDialog',
    'load_multiplicadores',
    'save_multiplicadores',
    'load_objetos_criterios',
    'save_objetos_criterios',
    'update_objeto_criterios',
    'get_objeto_criterios',
    'recalculate_all_objects',
    'get_pontuacao_from_descricao',
    'create_objetos_auditaveis',
    'CriteriosDialog',
    'CustomTableView',
    'ExcelModelManager',
    'load_config'
] 