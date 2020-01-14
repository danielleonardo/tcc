from manipula_arquivos \
    import listar_arquivos_acordaos_nao_tratados \
          , gravar_ementa \
          , gravar_acordao \
          , obter_conteudo_acordao \
          , criar_diretorios_arquivos_tratados
from bs4 import BeautifulSoup

def extrair_conteudo_acordao(arquivo):
    conteudo = obter_conteudo_acordao(arquivo)
    html = BeautifulSoup(conteudo, features='lxml')
    retorno = ''

    for tag in html.find_all(eh_ementa):
        tag.extract()

    return html.text


def eh_ementa(tag):
    return tag.has_attr('data-estilo-editor') \
    and tag.attrs['data-estilo-editor'] == 'Ementa'

def extrair_conteudo_ementa(arquivo):
    conteudo = obter_conteudo_acordao(arquivo)
    html = BeautifulSoup(conteudo, features='lxml')
    retorno = ''

    for tag in html.find_all(eh_ementa):
        retorno += tag.text

    return retorno

criar_diretorios_arquivos_tratados()
for arquivo in listar_arquivos_acordaos_nao_tratados():
    print('processando arquivo', arquivo)
    ementa = extrair_conteudo_ementa(arquivo)
    gravar_ementa(arquivo, ementa)
    acordao = extrair_conteudo_acordao(arquivo)
    gravar_acordao(arquivo, acordao)
