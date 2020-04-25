from manipula_arquivos import obter_conteudo_acordao, \
                              listar_arquivos_acordaos_tratados, \
                              obter_path_completo_acordao_tratado
from database_utils import DatabaseUtils

for acordao in  listar_arquivos_acordaos_tratados():
    print(acordao)
    with DatabaseUtils() as database:
        database.inserir_ou_atualizar_conteudo(
            acordao, 
            obter_conteudo_acordao(obter_path_completo_acordao_tratado(acordao)))