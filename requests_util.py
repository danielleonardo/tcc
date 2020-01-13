import requests
from data_utils import formatar_data_ddmmyyyy

class RenovarCookieException(Exception):
    def __init__(self, message):
        self.message = message

def gerar_header_request(cookie_anti_robo):
    return {'accept':'*/*','accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7','cache-control':'no-cache','content-type':'application/x-www-form-urlencoded; charset=UTF-8','pragma':'no-cache','x-requested-with':'XMLHttpRequest', 'Cookie': cookie_anti_robo }

def lancar_erro_se_cookie_expirado(response):
    if response.status_code == 401:
        raise RenovarCookieException('necessario renovar cookie')

def enviar_post(data, cookie_anti_robo):
    response = requests.post(url = 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet', data = data, headers = gerar_header_request(cookie_anti_robo))
    lancar_erro_se_cookie_expirado(response)
    return response.json()

def realizar_chamada_inicial(periodo, cookie_anti_robo):
    data = {'termoGeral': '',
            'juizRelator': '',
            'numeroProcesso': '',
            'orgaoJulgador': '',
            'dataPublicacaoDe': formatar_data_ddmmyyyy(periodo),
            'dataPublicacaoAte': formatar_data_ddmmyyyy(periodo),
            'tipo_pesquisa': 'aco_ee',
            'order': 'DESC',
            'field': ''}
    return enviar_post(data, cookie_anti_robo)

def realizar_chamada_proxima_pagina(cookie_anti_robo):
    data = {'pager': 'true', 'action': 'next', 'tipo_pesquisa': 'aco_ee' }
    return enviar_post(data, cookie_anti_robo)

def realizar_chamada_buscar_conteudo_acordao(acordao, cookie_anti_robo):
    resposta = requests.get(acordao['acordaoLink'], headers = gerar_header_request(cookie_anti_robo))
    lancar_erro_se_cookie_expirado(resposta)
    return resposta
