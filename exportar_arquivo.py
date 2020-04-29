from database_utils import DatabaseUtils

with DatabaseUtils() as db:
    db.exportar_arquivo('/Users/danielcosta/acordaos_ementas.csv')
