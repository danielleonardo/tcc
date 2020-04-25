from manipula_arquivos \
    import listar_arquivos_acordaos_nao_tratados \
          , gravar_ementa \
          , gravar_acordao \
          , obter_conteudo_acordao \
          , criar_diretorios_arquivos_tratados \
          , remover_ementas
from bs4 import BeautifulSoup
from unidecode import unidecode
import re

def extrair_conteudo_acordao(arquivo):
    conteudo = obter_conteudo_acordao(arquivo)
    html = BeautifulSoup(conteudo, features='lxml')
    for tag in html.find_all(eh_ementa):
        tag.extract()

    for tag in html.find_all(eh_cabecalho):
        tag.extract()

    for tag in html.find_all(eh_assinatura):
        tag.extract()

    return html.text


def eh_ementa(tag):
    return tag.has_attr('data-estilo-editor') \
    and tag.attrs['data-estilo-editor'] == 'Ementa'

def eh_cabecalho(tag):
    return tag.has_attr('data-estilo-editor') \
    and tag.attrs['data-estilo-editor'] == 'Texto cabeçalho'

def eh_assinatura(tag):
    return tag.has_attr('data-estilo-editor') \
    and tag.attrs['data-estilo-editor'] == 'Assinatura'

def extrair_texto_ementa(texto_ementa, lista_ementas):
            ementa_list = re.split('ementa\.|Ementa\.|EMENTA\.|ementa:|Ementa:|EMENTA:|\.| -| e | E |"|:', texto_ementa)
            ementa_final = ''
            for ementa in ementa_list:
                if (len(ementa) > 100):
                    ementa_final = ''
                    continue

                #Caso especial da abreaviacao Art. (ex: Art. 386 da CLT)
                if (ementa.strip().upper() == 'ART' or (len(ementa) > 0 and ementa[-1].isnumeric())):
                    ementa_final = ementa_final + ementa.strip().upper() + '.'
                    continue

                ementa_final = ementa_final + unidecode(ementa.strip().upper())

                if (len(ementa_final.strip()) > 0):
                    lista_ementas.append(ementa_final)

                ementa_final = ''

def extrair_conteudo_ementa(arquivo):
    conteudo = obter_conteudo_acordao(arquivo)
    html = BeautifulSoup(conteudo, features='lxml')
    retorno = []

    for tag in html.find_all(eh_ementa):
        #buscando pelo padrao <strong>TITULO EMENTA 1. TITULO EMENTA 2. ... </strong>
        for ementa_string in tag.find_all('strong'):
            extrair_texto_ementa(ementa_string.text[:100], retorno)
            break

        #Caso a lista esteja vazia, não encontrou a tag, neste caso, busca nos 100 primeiros caracteres
        if (len(retorno) == 0):
            extrair_texto_ementa(tag.text[:100], retorno)

    return retorno

criar_diretorios_arquivos_tratados()
remover_ementas()
for arquivo in listar_arquivos_acordaos_nao_tratados():
    print('processando arquivo', arquivo)
    ementas = extrair_conteudo_ementa(arquivo)
    print(ementas)
    acordao = extrair_conteudo_acordao(arquivo)
    acordao_tratado = gravar_acordao(arquivo, acordao)
    gravar_ementa(acordao_tratado, ementas)
