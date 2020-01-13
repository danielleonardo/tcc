import json
import os
from data_utils import formatar_data_yyyymmdd

diretorio_base = '/Users/danielcosta/desenv/tcc'

def formatar_nome_diretorio(periodo):
    return diretorio_base + "/" + formatar_data_yyyymmdd(periodo)
    
def criar_diretorio_periodo(periodo):
    nome_diretorio = formatar_nome_diretorio(periodo)

    if not os.path.exists(nome_diretorio):
         print('diretorio %s ainda nao existe. criando ', nome_diretorio)
         os.makedirs(nome_diretorio)

def obter_nome_arquivo_finalizado(periodo):
    return formatar_nome_diretorio(periodo) + '/finalizado.txt'

def chamada_ja_realizada(periodo):
    return os.path.exists(obter_nome_arquivo_finalizado(periodo))

def obter_nome_arquivo_acordaos(periodo):
    return formatar_nome_diretorio(periodo) + '/acordaos.json'

def obter_conteudo_acordaos(periodo):
    with (open(obter_nome_arquivo_acordaos(periodo), 'r')) as arquivo:
        return json.load(arquivo)

def apagar_arquivos_temporarios(periodo):
    if os.path.exists(obter_nome_arquivo_acordaos(periodo)):
        os.remove(obter_nome_arquivo_acordaos(periodo))

    if os.path.exists(obter_nome_arquivo_finalizado(periodo)):
        os.remove(obter_nome_arquivo_finalizado(periodo))

def obter_diretorio_arquivos():
    return diretorio_base + '/acordaos'

def gravar_conteudo_acordao(acordao, conteudo_acordao):
    nome_arquivo_conteudo_acordao = obter_nome_arquivo_conteudo_acordao(acordao)
    with(open(nome_arquivo_conteudo_acordao, 'w')) as arquivo:
        arquivo.write(conteudo_acordao)

def criar_diretorio_acordaos_se_nao_existir():
    if not os.path.exists(obter_diretorio_arquivos()):
        os.makedirs(obter_diretorio_arquivos())

def obter_nome_arquivo_conteudo_acordao(acordao):
    linkAcordao = acordao['acordaoLink'] 
    idDocumento = linkAcordao.split('docId=')[1].split('&')[0]
    return obter_diretorio_arquivos() + '/' + idDocumento + '.html'

def obter_conteudo_ja_existente_periodo(periodo):
    acordaos = {}
    acordaos['acordaos'] = []

    if os.path.exists(obter_nome_arquivo_acordaos(periodo)):
        acordaos = obter_conteudo_acordaos(periodo)

    return acordaos

def gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo):
    acordaos = obter_conteudo_ja_existente_periodo(periodo)
    acordaos['acordaos'].extend(retorno_chamada['listaAcordao'])
    
    with(open(obter_nome_arquivo_acordaos(periodo), 'w')) as outfile:
        json.dump(acordaos, outfile)

def gravar_finalizado(periodo):
    with(open(obter_nome_arquivo_finalizado(periodo), 'w')) as arquivo:
        arquivo.write('finalizado')

def conteudo_acordao_ja_buscado(acordao):
    if not os.path.exists(obter_nome_arquivo_conteudo_acordao(acordao)):
        return False
    else:
        print('acordao ja foi buscado ', obter_nome_arquivo_conteudo_acordao(acordao))
        return True
