import json
import os
import ntpath

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

def obter_conteudo_acordao(nome_arquivo):
    with open(nome_arquivo, 'r') as f:
        return f.read()

def obter_diretorio_ementas():
    return diretorio_base + '/ementas'

def obter_diretorio_acordaos():
    return diretorio_base + '/acordaos_tratados'

def obter_nome_arquivo_ementa(path_arquivo_original):
    nome_arquivo_original = ntpath.split(os.path.splitext(path_arquivo_original)[0])[1]
    return obter_diretorio_ementas() + '/' + nome_arquivo_original + '_ementa.html'

def obter_nome_arquivo_acordao(path_arquivo_original):
    nome_arquivo_original = ntpath.split(os.path.splitext(path_arquivo_original)[0])[1]
    return obter_diretorio_acordaos() + '/' + nome_arquivo_original + '_acordao.html'


def listar_arquivos_acordaos_nao_tratados():
    retorno = []

    for nome_arquivo in os.listdir(obter_diretorio_arquivos()):

        if nome_arquivo.endswith('.html'): 
            path_arquivo_original = obter_diretorio_arquivos() + '/' + nome_arquivo 

            if not os.path.exists(obter_nome_arquivo_ementa(path_arquivo_original)) \
            and not os.path.exists(obter_nome_arquivo_acordao(path_arquivo_original)):
                retorno.append(path_arquivo_original)
            else:
                print('arquivo ja tratado.', path_arquivo_original)

    return retorno

def gravar_ementa(nome_arquivo_original, conteudo):
    with(open(obter_nome_arquivo_ementa(nome_arquivo_original), 'w')) as output:
        output.write(conteudo)

def gravar_acordao(nome_arquivo_original, conteudo):
    with(open(obter_nome_arquivo_acordao(nome_arquivo_original), 'w')) as output:
        output.write(conteudo)

def criar_diretorios_arquivos_tratados():
    if not os.path.exists(obter_diretorio_acordaos()):
        os.makedirs(obter_diretorio_acordaos())

    if not os.path.exists(obter_diretorio_ementas()):
        os.makedirs(obter_diretorio_ementas())


