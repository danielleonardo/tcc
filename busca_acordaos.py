import os
import datetime
import random
import json
import time
import requests

#0 - Setar cookie anti robo'
cookie_anti_robo = 'valor_cookie'

def parse_data(strData):
    return datetime.datetime.strptime(strData, '%d/%m/%Y')
    
def formatar_data(data):
    return data.strftime('%Y%m%d')

def formatar_nome_diretorio(periodo):
    data_inicio = parse_data(periodo[0])
    data_fim = parse_data(periodo[1])
    return formatar_data(data_inicio) + '_' + formatar_data(data_fim)
    
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

def realizar_chamada_inicial(periodo):
    #2.2.1 - Realizar chamada conforme:  curl 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet' -XPOST -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8'  -H 'Cookie: auth-trt2-es-hml=dc9ac3518f7ecc9056a6b1c8da3f1c3b;' --data 'termoGeral=&juizRelator=&numeroProcesso=&orgaoJulgador=&dataPublicacaoDe=01%2F01%2F2019&dataPublicacaoAte=31%2F01%2F2019&tipo_pesquisa=aco_ee&order=DESC&field='
    str_retorno_chamada = '{"totalDocs":132,"start":0,"currentPage":1,"totalPages":2,"listaAcordao":[{"numeroUnico":"0023300-18.2003.5.02.0062"},{"numeroUnico":"0046300-62.2008.5.02.0065"},{"numeroUnico":"1000015-09.2016.5.02.0034"}],"acordaoBO":{"sortField":"","sortOrder":"DESC","dataPublicacaoDe":"2019-03-01","dataPublicacaoAte":"2019-03-01","acordao":{}}}'
    return parse_retorno_chamada(str_retorno_chamada)

def realizar_chamada_proxima_pagina():
   # Realizar chamada conforme curl 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet' -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'Accept: */*' -H 'Origin: http://search.trtsp.jus.br' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Referer: http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaosEletronicosEmentados.jsp' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' -H 'Cookie: JSESSIONID=456B7D7317C2C394B9C9C9E1AC8C06D4.easysearch01; _ga=GA1.3.453960748.1545014547; _gid=GA1.3.1109241380.1578597618; auth-trt2-es-hml=fe3d24a03fa685c073d82ea7872f8b05' --data 'pager=true&action=next&tipo_pesquisa=aco_ee' --compressed --insecure 
    str_retorno_chamada = '{"totalDocs":132,"start":0,"currentPage":2,"totalPages":2,"listaAcordao":[{"numeroUnico":"0023300-18.2003.5.02.0062"},{"numeroUnico":"0046300-62.2008.5.02.0065"},{"numeroUnico":"1000015-09.2016.5.02.0034"}],"acordaoBO":{"sortField":"","sortOrder":"DESC","dataPublicacaoDe":"2019-03-01","dataPublicacaoAte":"2019-03-01","acordao":{}}}'
    return parse_retorno_chamada(str_retorno_chamada)

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

def obter_numero_segundos():
    return random.randint(3, 15)

def aguardar_antes_de_proxima_chamada():
    segundos_a_aguardar = obter_numero_segundos()
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
            retorno_chamada = realizar_chamada_proxima_pagina()
            gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)
            pagina_atual = retorno_chamada['currentPage']
            aguardar_antes_de_proxima_chamada()
        
        gravar_finalizado(periodo)
    else:
        print('chamada ja realizada para o periodo', periodo)

    return obter_conteudo_acordaos(periodo)
   

lista_periodos = [('01/01/2019', '31/01/2019'), \
                  ('01/02/2019', '28/02/2019'), \
                  ('01/03/2019', '31/03/2019'), \
                  ('01/04/2019', '30/04/2019'), \
                 ]

for periodo in lista_periodos:
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
    aguardar_antes_de_proxima_chamada()


  
