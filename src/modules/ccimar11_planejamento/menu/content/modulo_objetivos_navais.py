from .objetivos_navais import (
    ClickableLabel,
    CriterioWidget,
    load_objetivos_navais_data,
    save_objetivos_navais_data,
    TreeLevelDelegate,
    CustomTreeView,
    DraggableListWidget,
    create_objetivos_navais
)
from .objetivos_navais.ui import create_objetivos_navais

def create_objetivos_navais(title_text):
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
    return create_objetivos_navais(title_text) 