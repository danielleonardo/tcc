import datetime
from datetime import timedelta

def parse_data(strData):
    return datetime.datetime.strptime(strData, '%d/%m/%Y')
    
def formatar_data_ddmmyyyy(data):
    return data.strftime('%d/%m/%Y')

def incrementar_periodo(periodo):
    return periodo + timedelta(days=1)

def formatar_data_yyyymmdd(data):
    return data.strftime('%Y%m%d')
