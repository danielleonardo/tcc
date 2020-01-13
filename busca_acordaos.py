import random
import time
import requests
from manipula_arquivos \
    import chamada_ja_realizada \
         , apagar_arquivos_temporarios \
         , gravar_retorno_pesquisa_acordaos \
         , gravar_finalizado \
         , obter_conteudo_acordaos \
         , conteudo_acordao_ja_buscado \
         , criar_diretorio_acordaos_se_nao_existir \
         , criar_diretorio_periodo \
         , gravar_conteudo_acordao
from data_utils import parse_data, formatar_data_ddmmyyyy, incrementar_periodo
         

class RenovarCookieException(Exception):
    def __init__(self, message):
        self.message = message

#0 - Setar cookie anti robo'
cookie_anti_robo = 'JSESSIONID=393ECA28803E7B4CDCE30DA4E14789FF.easysearch01; _ga=GA1.3.453960748.1545014547; _gid=GA1.3.1737234348.1578776541; auth-trt2-es-hml=625bd9045415b193ec2145c67dcc63c1'

data_inicial = '01/01/2019'
quantidade_dias = 365
quantidade_chamadas = 0

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
   
def buscar_conteudo(acordao):
    if not conteudo_acordao_ja_buscado(acordao):
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

#Inicio do procedimento
periodo = parse_data(data_inicial)    

criar_diretorio_acordaos_se_nao_existir()
for i in range(quantidade_dias):
    criar_diretorio_periodo(periodo)
    acordaos_periodo = pesquisar_acordaos(periodo)

    for acordao in acordaos_periodo['acordaos']:

        if not acordao['ementaLink']:
            continue

        buscar_conteudo(acordao)

    periodo = incrementar_periodo(periodo)
