import os
from database_utils import DatabaseUtils
from manipula_arquivos import listar_ementas, obter_diretorio_ementa

with DatabaseUtils() as database:
    for ementa in listar_ementas():
        diretorio_ementa = obter_diretorio_ementa(ementa)
        database.inserir_ementa_se_nao_existir(ementa)

        if (os.path.isdir(diretorio_ementa)):
            print(ementa)
            for acordao in os.listdir(diretorio_ementa):
                database.inserir_acordao_se_nao_existir(acordao)
                database.relacionar_ementa_acordao(ementa, acordao)
                print(acordao)
