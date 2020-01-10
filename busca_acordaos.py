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
cookie_anti_robo = 'JSESSIONID=45059672F2EFB562649597F145600A94.easysearch01; _ga=GA1.3.453960748.1545014547; _gid=GA1.3.1109241380.1578597618; auth-trt2-es-hml=301e3d9c7e23ed91332a13b0e18b935a'

data_inicial = '15/08/2019'
quantidade_dias = 90
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

def enviar_request(data):
    request = requests.post(url = 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet', data = data, headers = gerar_header_request())

    if request.status_code == 401:
        raise RenovarCookieException('necessario renovar cookie')
    
    return request.json()

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
    return enviar_request(data)

def realizar_chamada_proxima_pagina():
    data = {'pager': 'true', 'action': 'next', 'tipo_pesquisa': 'aco_ee' }
    return enviar_request(data)

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
        arquivo.write('finalizado');

def pesquisar_acordaos(periodo):
    print('pesquisando acordaos para periodo', periodo);
    retorno_chamada = None

    if not chamada_ja_realizada(periodo):
        apagar_arquivos_temporarios(periodo)
        retorno_chamada = realizar_chamada_inicial(periodo)
        gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)

        pagina_atual = retorno_chamada['currentPage']
        total_paginas = retorno_chamada['totalPages']
        
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
   
#Inicio do procedimento
periodo = parse_data(data_inicial)    
for i in range(quantidade_dias):
    criar_diretorio_periodo(periodo)
    #2.2 - Pesquisar acordaos do periodo
    acordaos_periodo = pesquisar_acordaos(periodo)
    print('acordaos buscados para periodo', acordaos_periodo)
    #2.3 - Para cada acordao:
    #2.3.1 - Buscar url no campo "acordaoLink"
    #2.3.2 - Realizar curl para buscar conteudo do acordao conforme: curl 'http://search.trtsp.jus.br/easysearch/cachedownloader?collection=coleta011&docId=0de2d597dbd9460bc4cd4c4b6fa28faebfb53707&fieldName=ementa&extension=html#q=' -H 'Cookie: auth-trt2-es-hml=dc9ac3518f7ecc9056a6b1c8da3f1c3b;'
    #2.3.3 - Buscar informacoes da ementa. Ex de retorno: <p style="padding-left: 200px; font-size: 12pt; float: none; margin-bottom: 6pt; line-height: 113%; font-family: 'Arial'; position: static; text-align: justify; text-indent: 0px;" data-estilo-editor="Ementa"><strong>MANUTEN&Ccedil;&Atilde;O DO PLANO DE SA&Uacute;DE. EX-EMPREGADO. APOSENTADO. ART. 31 DA LEI 9.656/1998. </strong>Ao aposentado que contribuir para plano de sa&uacute;de, em decorr&ecirc;ncia de v&iacute;nculo empregat&iacute;cio, pelo prazo m&iacute;nimo de dez anos, &eacute; assegurado o direito de manuten&ccedil;&atilde;o como benefici&aacute;rio, nas mesmas condi&ccedil;&otilde;es de cobertura assistencial de que gozava quando da vig&ecirc;ncia do contrato de trabalho, inclusive no que respeita aos valores praticados na ap&oacute;lice coletiva, desde que assuma o pagamento integral do seguro sa&uacute;de. Esta &eacute; a interpreta&ccedil;&atilde;o teleol&oacute;gica mais autorizada do art. 31 da Lei 9.656/1998. <strong>Recurso do reclamante provido neste aspecto.</strong></p>
    #2.3.4 - Gravar acordao sem a ementa no diretorio do respectivo periodo com o nome numeroUnicoProcesso (sem pontos ou tracos) _acordao.txt
    #2.3.5 - Gravar ementa no diretorio do respectivo periodo com o nome numeroUnicoProcesso_ementa.txt
    #2.4 - Aguardar um periodo aleatorio entre 1 e 5 segundos
    aguardar_antes_de_proxima_chamada(True)
    periodo = periodo + timedelta(days=1)
    i += 1


  
