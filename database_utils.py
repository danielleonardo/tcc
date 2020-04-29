import psycopg2

class DatabaseUtils:
    connection = None
 
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            user = "postgres",
            password = "123456",
            host = "localhost",
            port = "5432",
            database = "tcc")
        return self

    def __exit__(self, type, value, traceback):
        if (self.connection != None):
            self.connection.close()

    def executar_insert(self, insert, valores=()):
        cursor = self.connection.cursor()
        pg_insert = insert
        inserted_values = valores
        cursor.execute(pg_insert, inserted_values)
        cursor.close()
        self.connection.commit()

    def inserir_acordao_se_nao_existir(self, acordao):
        self.executar_insert("INSERT INTO acordao (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING;", (acordao,))

    def inserir_ementa_se_nao_existir(self, ementa):
        self.executar_insert("INSERT INTO ementa (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING;", (ementa,))

    def inserir_ou_atualizar_conteudo(self, acordao, conteudo):
        self.executar_insert("""INSERT 
                                  INTO acordao_conteudo (nome_acordao, conteudo) 
                                SELECT %s, %s
                                  FROM acordao 
                                 WHERE nome = %s
                           ON CONFLICT (nome_acordao) 
                         DO UPDATE SET conteudo = EXCLUDED.conteudo;""", (acordao, conteudo, acordao))

    def relacionar_ementa_acordao(self, ementa, acordao):
        self.executar_insert("""INSERT 
                                  INTO acordao_ementa (nome_acordao, nome_ementa) 
                                VALUES (%s, %s) 
                           ON CONFLICT (nome_acordao, nome_ementa) DO NOTHING;""", (acordao, ementa,))

    def limpar_base(self):
        self.executar_insert("""
            truncate acordao_ementa cascade;
            truncate acordao_conteudo cascade;
            truncate ementa cascade;
            truncate acordao cascade;""")

    def exportar_arquivo(self, caminho):
        self.executar_insert("""Copy (select a.nome_acordao, regexp_replace(a.conteudo, E'[\\n\\r]+', ' ', 'g' )
, (select count(distinct ae2.nome_acordao )
     from acordao_ementa ae2 
    where ae2.nome_acordao = a.nome_acordao and ae2.nome_ementa = 'RESPONSABILIDADE SUBSIDIARIA') as "ementa_responsabilidade_subsidiaria"
, (select count(distinct ae2.nome_acordao ) 
     from acordao_ementa ae2 
    where ae2.nome_acordao = a.nome_acordao and ae2.nome_ementa = 'HORAS EXTRAS') as "ementa_horas_extras"
, (select count(distinct ae2.nome_acordao )
     from acordao_ementa ae2 
    where ae2.nome_acordao = a.nome_acordao and ae2.nome_ementa = 'JUSTICA GRATUITA') as "ementa_justica_gratuita"
, (select count(distinct ae2.nome_acordao )
     from acordao_ementa ae2 
    where ae2.nome_acordao = a.nome_acordao and ae2.nome_ementa = 'EMBARGOS DE DECLARACAO') as "ementa_embargos_de_declaracao"
, (select count(distinct ae2.nome_acordao )
     from acordao_ementa ae2 
    where ae2.nome_acordao = a.nome_acordao and ae2.nome_ementa = 'ONUS DA PROVA') as "ementa_onus_da_prova"    
from acordao_conteudo a
where exists (select 1 
                from acordao_ementa ae 
               where ae.nome_acordao  = a.nome_acordao 
                 and (ae.nome_ementa in('RESPONSABILIDADE SUBSIDIARIA',  
                                        'HORAS EXTRAS', 
                                        'JUSTICA GRATUITA', 
                                        'EMBARGOS DE DECLARACAO', 
                                        'ONUS DA PROVA')))) To '%s' With CSV DELIMITER ',' HEADER;
        """ % caminho)
