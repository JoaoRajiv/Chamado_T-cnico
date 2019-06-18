import psycopg2

class Conexao:
    @staticmethod
    def criar_conexao():
        conexao = psycopg2.connect(
            host="localhost",
            port=5433,
            database="chamado",
            user="postgres",
            password="1234"
        )
        conexao.autocommit = True
        return conexao