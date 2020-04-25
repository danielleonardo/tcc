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
from data_utils \
    import parse_data \
         , formatar_data_ddmmyyyy \
         , incrementar_periodo
from requests_util \
    import RequestUtils, RenovarCookieException
from controlador_tempo_requests import ControladorTempoRequests
from send_mail import send_mail_token_expirado
from create_gui import Alerta

#0 - Setar cookie anti robo'
cookie_anti_robo = 'JSESSIONID=E8294CF8A8D785F6A0FB39DC681B353B.easysearch01; auth-trt2-es-hml=541333d44114ef6cf2b7edde25af298a'

controlador_tempo_requests = ControladorTempoRequests()
requests_util = RequestUtils(cookie_anti_robo)

def pesquisar_acordaos(periodo):
    print('pesquisando acordaos para periodo', periodo)
    retorno_chamada = None

    if not chamada_ja_realizada(periodo):
        apagar_arquivos_temporarios(periodo)
        retorno_chamada = requests_util.realizar_chamada_inicial(periodo)
        gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)
        pagina_atual = retorno_chamada['currentPage']
        total_paginas = retorno_chamada['totalPages']
        controlador_tempo_requests.aguardar_antes_de_proxima_chamada()
        
        while pagina_atual < total_paginas:
            try:
                retorno_chamada = requests_util.realizar_chamada_proxima_pagina()
                gravar_retorno_pesquisa_acordaos(retorno_chamada, periodo)
                pagina_atual = retorno_chamada['currentPage']
                controlador_tempo_requests.aguardar_antes_de_proxima_chamada()
            except RenovarCookieException:
                send_mail_token_expirado()
                Alerta()
                raise
            except:
                controlador_tempo_requests.aguardar_antes_de_proxima_chamada(True)
        
        gravar_finalizado(periodo)
    else:
        print('chamada ja realizada para o periodo', periodo)

    return obter_conteudo_acordaos(periodo)
   
def buscar_conteudo(acordao):
    if not conteudo_acordao_ja_buscado(acordao):
        print('buscando conteudo para acordao', acordao)
        print('link acordao:', acordao['acordaoLink'])
        try:
            resposta = requests_util.realizar_chamada_buscar_conteudo_acordao(acordao)
            gravar_conteudo_acordao(acordao, resposta.text)
            controlador_tempo_requests.aguardar_antes_de_proxima_chamada()
        except RenovarCookieException:
            send_mail_token_expirado()
            Alerta()
            raise
        except:
            print('Erro ao buscar conteudo. Aguardando.')
            controlador_tempo_requests.aguardar_antes_de_proxima_chamada(True)

#Inicio do procedimento
periodo = parse_data('01/01/2016')
criar_diretorio_acordaos_se_nao_existir()
for i in range(365):
    criar_diretorio_periodo(periodo)
    acordaos_periodo = pesquisar_acordaos(periodo)

    for acordao in acordaos_periodo['acordaos']:

        if not acordao['ementaLink']:
            continue

        buscar_conteudo(acordao)

    periodo = incrementar_periodo(periodo)
