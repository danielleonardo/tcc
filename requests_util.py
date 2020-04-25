import requests
from data_utils import formatar_data_ddmmyyyy
from controlador_tempo_requests import ControladorTempoRequests 

class RenovarCookieException(Exception):

    def __init__(self, message):
        self.message = message

class RequestUtils:
    controladorRequests = ControladorTempoRequests()

    def __init__(self, cookie_anti_robo):
        self.cookie_anti_robo = cookie_anti_robo
        self.url_post = 'http://search.trtsp.jus.br/EasySearchFrontEnd/AcordaoServlet'

    def gerar_header_request(self):
        return {'accept':'*/*',
                'accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control':'no-cache',
                'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                'pragma':'no-cache',
                'x-requested-with':'XMLHttpRequest', 
                'Cookie': self.cookie_anti_robo }

    def lancar_erro_se_cookie_expirado(self, response):
        if response.status_code == 401:
            raise RenovarCookieException('necessario renovar cookie')

    def enviar_post(self, data):
        response = requests.post(url = self.url_post, \
                                 data = data, \
                                 headers = self.gerar_header_request())
        self.lancar_erro_se_cookie_expirado(response)
        return response.json()

    def realizar_chamada_inicial(self, periodo):
        while(True):
            try: 
                data = {'termoGeral': '',
                        'juizRelator': '',
                        'numeroProcesso': '',
                        'orgaoJulgador': '',
                        'dataPublicacaoDe': formatar_data_ddmmyyyy(periodo),
                        'dataPublicacaoAte': formatar_data_ddmmyyyy(periodo),
                        'tipo_pesquisa': 'aco_ee',
                        'order': 'DESC',
                        'field': ''}
                return self.enviar_post(data)
            except RenovarCookieException:
                raise
            except Exception as ex:
                print('Erro ao realizar chamada inicial', ex)
                self.controladorRequests.aguardar_antes_de_proxima_chamada(True)



    def realizar_chamada_proxima_pagina(self):
        while(True):
            try:
                data = {'pager': 'true', 'action': 'next', 'tipo_pesquisa': 'aco_ee' }
                return self.enviar_post(data)
            except RenovarCookieException:
                raise
            except Exception as ex:
                print('Erro ao buscar próxima página', ex)
                self.controladorRequests.aguardar_antes_de_proxima_chamada(True)

    def realizar_chamada_buscar_conteudo_acordao(self, acordao):
        resposta = requests.get(acordao['acordaoLink'], headers = self.gerar_header_request())
        self.lancar_erro_se_cookie_expirado(resposta)
        return resposta
