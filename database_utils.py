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