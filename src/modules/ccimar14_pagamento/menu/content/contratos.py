from .modulo_contratos import (    
    CustomTableView,
    ExcelModelManager,
    load_config
)
from .modulo_contratos.ui import create_vigencia_contratos

def create_vigencia_contratos(title_text):
    """
    Cria a interface para objetos auditáveis usando a versão modularizada.
    
    Esta função é um wrapper para a função create_objetos_auditaveis do módulo ui,
    mantendo a mesma assinatura para compatibilidade com o código existente.
    
    Args:
        title_text (str): Texto do título
        database_model: Modelo de banco de dados
        
    Returns:
        QFrame: Frame contendo a interface de objetos auditáveis
    """
    return create_vigencia_contratos(title_text) 