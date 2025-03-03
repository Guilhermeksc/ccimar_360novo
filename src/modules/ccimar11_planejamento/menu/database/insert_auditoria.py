from PyQt6.QtSql import QSqlQuery
import pandas as pd

def insert_auditoria(db, cod_siafi, ano_auditoria):
    """Registers an audit for a Military Organization."""
    query = QSqlQuery(db)

    query.prepare("SELECT id_om FROM organizacoes_militares WHERE cod_siafi = ?")
    query.addBindValue(cod_siafi)
    if not query.exec() or not query.next():
        print(f"Error: Military Organization not found for SIAFI code {cod_siafi}")
        return

    id_om = query.value(0)

    sql = """
    INSERT INTO auditorias (id_om, ano_auditoria)
    VALUES (?, ?)
    """
    query.prepare(sql)
    query.addBindValue(id_om)
    query.addBindValue(ano_auditoria)

    if not query.exec():
        print("Error inserting Audit:", query.lastError().text())
    else:
        print(f"Audit for year {ano_auditoria} registered for OM {cod_siafi}.")
