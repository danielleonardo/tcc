import random
import time

class ControladorTempoRequests:

    def __init__(self):
        self.quantidade_chamadas = 0

    def zerar_quantidade_chamadas(self):
        self.quantidade_chamadas = 0

    def incrementar_quantidade_chamadas(self):
        self.quantidade_chamadas += 1

    def obter_numero_segundos(self, periodo_longo):
        if periodo_longo or self.quantidade_chamadas > 10:
            self.zerar_quantidade_chamadas()
            return random.randint(4, 5)
        else:
            self.incrementar_quantidade_chamadas()
            return random.randint(1, 3)

    def aguardar_antes_de_proxima_chamada(self, periodo_longo = False):
        segundos_a_aguardar = self.obter_numero_segundos(periodo_longo)
        print('aguardando', segundos_a_aguardar, 'segundos antes da proxima chamada')
        time.sleep(segundos_a_aguardar)
