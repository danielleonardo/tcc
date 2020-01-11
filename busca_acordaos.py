import os
import datetime
from datetime import timedelta
import random
import json
import time
import requests

class RenovarCookieException(Exception):
    def __init__(self, message):
        self.message = message

#0 - Setar cookie anti robo'
cookie_anti_robo = 'JSESSIONID=EE11BE52AA63D454D4ACD3F1BE7B6977.easysearch01; _ga=GA1.3.453960748.1545014547; auth-trt2-es-hml=ca4669e060fbea28e0699896733c1700'

data_inicial = '01/01/2019'
quantidade_dias = 365
quantidade_chamadas = 0
diretorio_base = '/Users/danielcosta/desenv/tcc'

def parse_data(strData):
    return datetime.datetime.strptime(strData, '%d/%m/%Y')
    
def formatar_data_yyyymmdd(data):
    return data.strftime('%Y%m%d')

def formatar_data_ddmmyyyy(data):
    return data.strftime('%d/%m/%Y')

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

def parse_retorno_chamada(str_retorno_chamada):
    print('parse_retorno_chamada:', str_retorno_chamada)
    return json.loads(str_retorno_chamada)

def gerar_header_request():
    return {'accept':'*/*','accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7','cache-control':'no-cache','content-type':'application/x-www-form-urlencoded; charset=UTF-8','pragma':'no-cache','x-requested-with':'XMLHttpRequest', 'Cookie': cookie_anti_robo }

def lancar_erro_se_cookie_expirado(response):
    if response.status_code == 401:
        raise RenovarCookieException('necessario renovar cookie')

def enviar_post(data):
    response = requests.post(url = 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet', data = data, headers = gerar_header_request())
    lancar_erro_se_cookie_expirado(response)
    return response.json()

def realizar_chamada_inicial(periodo):
    data = {'termoGeral': '',
            'juizRelator': '',
            'numeroProcesso': '',
            'orgaoJulgador': '',
            'dataPublicacaoDe': formatar_data_ddmmyyyy(periodo),
            'dataPublicacaoAte': formatar_data_ddmmyyyy(periodo),
            'tipo_pesquisa': 'aco_ee',
            'order': 'DESC',
            'field': ''}
    return enviar_post(data)

def realizar_chamada_proxima_pagina():
    data = {'pager': 'true', 'action': 'next', 'tipo_pesquisa': 'aco_ee' }
    return enviar_post(data)

def obter_nome_arquivo_acordaos(periodo):
    return formatar_nome_diretorio(periodo) + '/acordaos.json'

def obter_conteudo_acordaos(periodo):
    with (open(obter_nome_arquivo_acordaos(periodo), 'r')) as arquivo:
        return json.load(arquivo)

def gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo):
    nome_arquivo_acordaos = obter_nome_arquivo_acordaos(periodo)
    acordaos = {}
    acordaos['acordaos'] = []
    if os.path.exists(nome_arquivo_acordaos):
        acordaos = obter_conteudo_acordaos(periodo)

    acordaos['acordaos'].extend(retorno_chamada['listaAcordao'])
    
    with(open(nome_arquivo_acordaos, 'w')) as outfile:
        json.dump(acordaos, outfile)
    
def apagar_arquivos_temporarios(periodo):
    if os.path.exists(obter_nome_arquivo_acordaos(periodo)):
        os.remove(obter_nome_arquivo_acordaos(periodo))

    if os.path.exists(obter_nome_arquivo_finalizado(periodo)):
        os.remove(obter_nome_arquivo_finalizado(periodo))

def zerar_quantidade_chamadas():
    global quantidade_chamadas
    quantidade_chamadas = 0

def incrementar_quantidade_chamadas():
    global quantidade_chamadas
    quantidade_chamadas = quantidade_chamadas + 1

def obter_numero_segundos(periodo_longo):
    if periodo_longo or quantidade_chamadas > 10:
        zerar_quantidade_chamadas()
        return random.randint(4, 5)
    else:
        incrementar_quantidade_chamadas()
        return random.randint(1, 3)

def aguardar_antes_de_proxima_chamada(periodo_longo = False):
    segundos_a_aguardar = obter_numero_segundos(periodo_longo)
    print('aguardando', segundos_a_aguardar, 'segundos antes da proxima chamada')
    time.sleep(segundos_a_aguardar)

def gravar_finalizado(periodo):
    with(open(obter_nome_arquivo_finalizado(periodo), 'w')) as arquivo:
        arquivo.write('finalizado')

def pesquisar_acordaos(periodo):
    print('pesquisando acordaos para periodo', periodo)
    retorno_chamada = None

    if not chamada_ja_realizada(periodo):
        apagar_arquivos_temporarios(periodo)
        retorno_chamada = realizar_chamada_inicial(periodo)
        gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)

        pagina_atual = retorno_chamada['currentPage']
        total_paginas = retorno_chamada['totalPages']
        aguardar_antes_de_proxima_chamada()
        
        while pagina_atual < total_paginas:
            try:
                retorno_chamada = realizar_chamada_proxima_pagina()
                gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)
                pagina_atual = retorno_chamada['currentPage']
                aguardar_antes_de_proxima_chamada()
            except RenovarCookieException:
                raise
            except:
                aguardar_antes_de_proxima_chamada(True)
        
        gravar_finalizado(periodo)
    else:
        print('chamada ja realizada para o periodo', periodo)

    return obter_conteudo_acordaos(periodo)
   
def obter_diretorio_arquivos():
    return diretorio_base + '/acordaos'

def obter_nome_arquivo_conteudo_acordao(acordao):
    linkAcordao = acordao['acordaoLink'] 
    idDocumento = linkAcordao.split('docId=')[1].split('&')[0]
    return obter_diretorio_arquivos() + '/' + idDocumento + '.html'

def buscar_conteudo(acordao):
    if not os.path.exists(obter_nome_arquivo_conteudo_acordao(acordao)):
        print('buscando conteudo para acordao', acordao)
        print('link acordao:', acordao['acordaoLink'])
        try:
            resposta = requests.get(acordao['acordaoLink'], headers = gerar_header_request())
            lancar_erro_se_cookie_expirado(resposta)
            gravar_conteudo_acordao(acordao, resposta.text)
            aguardar_antes_de_proxima_chamada()
        except RenovarCookieException:
            raise
        except:
            print('Erro ao buscar conteudo. Aguardando.')
            aguardar_antes_de_proxima_chamada(True)
    else:
        print('acordao ja foi buscado ', obter_nome_arquivo_conteudo_acordao(acordao))

def gravar_conteudo_acordao(acordao, conteudo_acordao):
    nome_arquivo_conteudo_acordao = obter_nome_arquivo_conteudo_acordao(acordao)
    with(open(nome_arquivo_conteudo_acordao, 'w')) as arquivo:
        arquivo.write(conteudo_acordao)

#Inicio do procedimento
periodo = parse_data(data_inicial)    

if not os.path.exists(obter_diretorio_arquivos()):
    os.makedirs(obter_diretorio_arquivos())

for i in range(quantidade_dias):
    criar_diretorio_periodo(periodo)
    acordaos_periodo = pesquisar_acordaos(periodo)

    for acordao in acordaos_periodo['acordaos']:

        if not acordao['ementaLink']:
            continue

        buscar_conteudo(acordao)

    periodo = periodo + timedelta(days=1)

