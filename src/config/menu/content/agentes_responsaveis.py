from .modulo_agentes_responsaveis.ui import (
    create_agentes_responsaveis
)

def create_agentes_responsaveis(title_text, icons):
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
    return create_agentes_responsaveis(title_text, icons) 