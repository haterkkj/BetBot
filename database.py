import mysql.connector
import os
from dotenv import load_dotenv
import datetime
import time
from zoneinfo import ZoneInfo

#carrega valores do arquivo env
load_dotenv()
HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')

#cria a pool de conexoes
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name='mypool',
    pool_size=5,
    host = HOST,
    user = USER,
    password = PASSWORD,
    database = DATABASE
)

class DatabaseManager():
    def __init__(self):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name='mypool',
            pool_size=5,
            host = HOST,
            user = USER,
            password = PASSWORD,
            database = DATABASE
        )
        self.conexao = None

    def iniciar_transacao(self):
        '''
            Abre uma transação. É necessário abrir uma transação toda vez que for executar uma query.
        '''
        try:
            self.conexao = self.pool.get_connection()
            self.conexao.start_transaction()
        except mysql.connector.Error as e:
            print(f'''Erro ao iniciar transação: 
                  {e}
                ''')

    def faz_commit(self):
        '''
            Realiza um commit da transação aberta e em seguida encerra a transação anteriormente aberta.
        '''

        if not self.conexao:
            raise Exception('Transação não iniciada. Use a função "iniciar_transacao()" antes de commitar.')
        
        try:
            self.conexao.commit()
        except mysql.connector.Error as e:
            print(f'''Não foi possível commitar as mudanças devido ao seguinte erro:
                  {e}
                  ''')
            return False
        finally:
            self.conexao.close()
            self.conexao = None
        return True
    
    def faz_rollback(self):
        '''
            Realiza um rollback da transação aberta e em seguida encerra a transação anteriormente aberta.
        '''

        if not self.conexao:
            raise Exception('Transação não iniciada. Use a função "iniciar_transacao()" antes de fazer rollback.')
        
        try:
            self.conexao.rollback()
        except mysql.connector.Error as e:
            print(f'''Não foi possível reverter as mudanças devido ao seguinte erro:
                  {e}
                  ''')
            return False
        finally:
            self.conexao.close()
            self.conexao = None
        return True
    
    def realizar_insert(self, tabela, colunas, valores):
        '''
            Se conecta ao Banco de Dados e realiza um insert na tabela e colunas informadas
            informadas com os valores passados. 
            :param tabela: recebe o nome da tabela na qual será inserido algum valor
            :param colunas: recebe um array com o(s) nome(s) da(s) coluna(s) na qual estaremos inserindo algum valor
            :param valores: recebe um array com o(s) valor(es) que estaremos inserindo na(s) coluna(s) informada(s).
                            Atenção: A ordem na qual são informadas as colunas é a ordem na qual são inseridos
                            os valores. 

            :return: retorna um valor tipo boolean caso a operação não seja realizada com sucesso ou não.
        '''

        if not self.conexao:
            raise Exception('Transação não iniciada. Use a função "iniciar_transacao()" primeiro.')
        
        colunas_str = ', '.join(colunas)
        valores_placeholder = ', '.join(['%s']*len(valores))

        query = f'insert into {tabela} ({colunas_str}) values ({valores_placeholder})'
        try:
            cursor = self.conexao.cursor()
            cursor.execute(query, valores)
            return True
        except mysql.connector.Error as e:
            print(f'''Não foi possivel realizar o insert devido ao seguinte erro:
                {e}
                ''')
            return False

    def realizar_select(self, tabela, colunas='*', condicao=None, join=None, ordem=None):
        '''
            Se conecta ao Banco de Dados e realiza update nas rows da tabela
            informada caso forem compativeis as condições passadas.
            :param tabela: recebe o nome da tabela na qual será selecionado algum valor
            :param colunas: recebe o nome das colunas que estaremos recuperando,
                            caso vazia, é entendido como '*'.
            :param condicao: recebe a condição para que o select seja realizado ou não
            :param join: recebe o 'inner join' do select caso seja necessario ou não
            :param ordem: recebe a ordem que sera mostrada os itens recuperados ou não 
            :return: retorna o conteudo do select ou um valor tipo boolean caso
                     a operação não seja realizada com sucesso.
        '''
        if not self.conexao:
            raise Exception('Transação não iniciada. Use a função "iniciar_transacao()" primeiro.')
        
        colunas_str = ', '.join(colunas)
        query = f'select {colunas_str} from {tabela}'
        if join:
            query += f' {join}'
        if condicao:
            query += f' where {condicao}'
        if ordem:
            query += f' order by {ordem};'
            
        try:
            cursor = self.conexao.cursor(dictionary=True)
            cursor.execute(query)
            resultados=cursor.fetchall()
            return resultados if resultados else None
        except mysql.connector.Error as e:
            print(f'''Não foi possivel realizar o select devido ao seguinte erro:
                {e}
                ''')
            return False

    def realizar_update(self, tabela, colunas_valores, condicao):
        '''
            Se conecta ao Banco de Dados e realiza update nas rows da tabela
            informada caso forem compativeis as condições passadas.
            :param tabela: recebe o nome da tabela na qual será atualizado algum valor
            :param colunas_valores: recebe o nome das colunas a serem alteradas e o novo valor para elas
                                    Ex.: 'nome = "novo nome"'
            :param condicao: recebe a condição para que o update seja realizado
            :return: retorna um valor do tipo boolean para o caso de a operação
                     ter dado certo ou errado.
        '''
        if not self.conexao:
            raise Exception('Transação não iniciada. Use a função "iniciar_transacao()" primeiro.')
        
        query=f'update {tabela} set {colunas_valores} where {condicao}'
        try:
            cursor = self.conexao.cursor()
            cursor.execute(query)
            return True
        except mysql.connector.Error as e:
            print(f'''Não foi possivel fazer o update em {tabela} por causa do seguinte erro: 
                {e}
                ''')
            return False

    def realizar_delete(self, tabela, condicao):
        '''
            Se conecta ao Banco de Dados e deleta rows na tabela onde
            as condições forem preenchidas.
            :param tabela: recebe o nome da tabela na qual será deletado algo
            :param condicao: recebe a condição para que o delete seja realizado
            :return: retorna um valor do tipo boolean para o caso de a operação
                     ter dado certo ou errado.
        '''
        query=f'delete from {tabela} where {condicao}'
        try:
            cursor = self.conexao.cursor()
            cursor.execute(query)
            return True
        except mysql.connector.Error as e:
            print(f'''Não foi possivel fazer o delete em {tabela} por causa do seguinte erro: 
                {e}
                ''')
            return False

def criar_tabelas():
    '''
        Se conecta ao Banco de Dados e cria tabelas dentro do Schema
        caso não existirem.
    '''
    try:
        conexao = pool.get_connection()
        cursor = conexao.cursor()
        cursor.execute('''create table if not exists aposta(
                            id int not null primary key auto_increment,
                            user_id bigint not null,
                            jogo_id int not null,
                            palpite varchar(255) not null,
                            valor_aposta float not null,
                            data_da_aposta datetime not null
                        );
                    ''')
        cursor.execute('''create table if not exists jogos(
                            id int not null primary key auto_increment,
                            time1 varchar(255) not null,
                            time2 varchar(255) not null,
                            resultado varchar(255),
                            campeonato varchar(500),
                            data_do_jogo datetime not null
                        );
                    ''')
        cursor.execute('''create table if not exists usuario(
                            id bigint not null primary key,
                            saldo float
                        );
                    ''')
        cursor.execute('''create table if not exists transacoes(
                            id bigint not null auto_increment primary key,
                            user_id bigint not null,
                            tipo_transacao varchar(50) not null,
                            data_da_transacao datetime not null,
                            saldo_antes float not null,
                            saldo_depois float not null,
                            foreign key (user_id) references usuario(id)
                        );
                    ''')
        conexao.commit()
    except mysql.connector.Error as e:
        print(f'''Não foi possivel criar as tabelas devido ao seguinte erro:
              {e}
              ''')
    finally:
        cursor.close()
        conexao.close()

def retorna_data_hora_no_formato_do_bd():
    '''
        Retorna data e hora atual de São Paulo no formato adequado
        para o realizar operações no BD.
    '''
    now = datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    return now