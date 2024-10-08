import datetime
import time
import schedule
import database
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebScrapJogos():
    def __init__(self):
        pass

    def agenda_scraping(self):
        '''
            Esta função é responsável por agendar o scraping, definindo a hora
            em que o programa deve executar as funções da rotina.
        '''
        schedule.every().day.at('03:00').do(self.executa_scraping)
        print('Rotina de scraping agendada.')
        while True:
            schedule.run_pending()
            time.sleep(60)

    def executa_scraping(self):
        '''
            Está função é responsável por realizar os trabalhos do dia e do dia anterior
        '''
        self.realiza_trabalho_da_rotina_diaria('hoje')
        self.realiza_trabalho_da_rotina_diaria('ontem')

    def realiza_trabalho_da_rotina_diaria(self, dia: str):
        '''
            Esta função é responsável por percorrer uma rotina de trabalhos.
            Os trabalhos da rotina dependem de seu parametro "dia", podendo realizar
            trabalhos de "hoje" ou "ontem".
            :param dia: recebe uma string, os valores esperados são "hoje" ou "ontem"
        '''
        service = Service()
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

        hoje = datetime.date.today()
        ontem = hoje - datetime.timedelta(days=1)

        if dia == 'hoje':
            data = hoje
        elif dia == 'ontem':
            data = ontem

        self.data_formato_bd = data.strftime('%Y-%m-%d')
        data = str(data.strftime('%d-%m-%Y'))
        url = f'https://ge.globo.com/agenda/#/futebol/{data}'
    
        driver.get(url)
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sportFeedstyle__Container-sc-n2f7bo-0'))
        )

        lista_buttons = section.find_elements(By.CLASS_NAME, 'ShowMoreButtonstyle__ShowMoreText-sc-15u0g3u-1')
        for button in lista_buttons:
            button.click()

        if dia == 'hoje':
            times_dos_jogos = self.recupera_nome_times_do_jogo(section)
            horario_dos_jogos = self.recupera_data_hora_dos_jogos(section)
            campeonato_dos_jogos = self.recupera_campeonato_dos_jogos(section)
            self.insere_jogos_de_hoje_no_bd(times_dos_jogos, campeonato_dos_jogos, horario_dos_jogos)
        else:
            jogos_de_ontem = self.recupera_nome_times_do_jogo(section)
            campeonato_jogos_ontem = self.recupera_campeonato_dos_jogos(section)
            horario_dos_jogos_ontem = self.recupera_data_hora_dos_jogos(section)
            resultado_dos_jogos = self.recupera_resultado_dos_jogos_ontem(section)
            self.atualiza_resultados_jogos_de_ontem_no_bd(jogos_de_ontem, campeonato_jogos_ontem, horario_dos_jogos_ontem, resultado_dos_jogos)

    def recupera_data_hora_dos_jogos(self, section):
        '''
            Esta função percorre a section recebida como parametro e armazena a data
            de todos os jogos do dia em um array. As datas são formatadas com o formato
            especifíco para uso no BD.
            :param section: section na qual será buscado os elementos
            :return: array com todos os horarios encontrados na página já formatados
        '''
        infos_jogo = section.find_elements(By.CLASS_NAME, 'sc-jXbUNg')
        horario_jogos_formatados = []
        for info_jogo in infos_jogo:
            if ':' in info_jogo.text:
                horario_jogos_formatados.append(self.data_formato_bd + ' ' + info_jogo.text.replace(':', '-') + '-00')
        return horario_jogos_formatados

    def recupera_nome_times_do_jogo(self, section):
        '''
            Esta função percorre a section recebida como parametro e armazena o nome
            dos dois times de cada jogo encontrado na página.
            :param section: section na qual será buscado os elementos
            :return: objeto com o nome dos dois times de cada jogo
        '''
        nome_times = section.find_elements(By.CLASS_NAME, 'sc-eeDRCY')
        nome_times_do_jogo = []
        i = 0 
        for nome_time in nome_times:
            if i < 1:
                jogo = {'time1': nome_time.text, 'time2': None}
                i += 1
            else:
                jogo['time2'] = nome_time.text
                nome_times_do_jogo.append(jogo)
                i = 0
        return nome_times_do_jogo

    def recupera_campeonato_dos_jogos(self, section):
        '''
            Esta função percorre a section recebida como parametro e armazena o nome
            do campeonato ao qual pertence cada um dos jogos do dia.
            :param section: section na qual será buscado os elementos
            :return: array com o campeonato de cada um dos jogos do dia
        '''
        campeonato_do_jogo = []
        campeonato = None
        times_vistos = 0
        for element in section.find_elements(By.XPATH, '//*[contains(@class, "eventGrouperstyle__ChampionshipName-sc-1bz1qr-2") or contains(@class, "sc-eeDRCY")]'):
            if 'eventGrouperstyle__ChampionshipName-sc-1bz1qr-2' in element.get_attribute('class'):
                campeonato = element.text
            elif 'sc-eeDRCY' in element.get_attribute('class') and campeonato:
                times_vistos += 1
                if times_vistos == 2:
                    campeonato_do_jogo.append(campeonato)
                    times_vistos = 0
        return campeonato_do_jogo
    
    def recupera_resultado_dos_jogos_ontem(self, section):
        '''
            Esta função percorre a section recebida como parametro e verifica 
            qual time venceu a partida com base em quem fez mais ou menos gol.
            Caso a quantidade de gols de ambos times do jogo forem iguais, é declarado empate.
            Esta função somente funcionará da forma correta se o dia informado na rotina for "ontem".
            :param section: section na qual será buscado os elementos
            :return: array com o resultados de todos os jogos do dia anterior.
        '''
        gols_dos_jogos = []
        resultado_dos_jogos = []
        i=0
        for element in section.find_elements(By.CLASS_NAME, 'sc-jsJBEP'):
            gols_dos_jogos.append(element.text)
            i += 1
            if i >= 2:
                if gols_dos_jogos[-2] > gols_dos_jogos[-1]:
                    resultado_dos_jogos.append('time1')
                elif gols_dos_jogos[-2] < gols_dos_jogos[-1]:
                    resultado_dos_jogos.append('time2')
                else:
                    resultado_dos_jogos.append('empate')
                i=0
        return resultado_dos_jogos
    
    def insere_jogos_de_hoje_no_bd(self, jogos_do_dia, campeonato_jogos, data_hora_jogos):
        '''
            Esta função insere no banco de dados os jogos que ocorrerão no dia.
            :param jogos_do_dia: objeto contendo o nome dos dois times de cada jogo
            :param campeonato_jogos: array contendo o nome dos campeonatos de cada jogo
            :param data_hora_jogos: array contendo a data e hora que cada jogo ocorrerá.
        '''
        db = database.DatabaseManager()
        db.iniciar_transacao()
        for jogo_do_dia, campeonato_jogo, data_hora_jogo in zip(jogos_do_dia, campeonato_jogos, data_hora_jogos):
            insert = db.realizar_insert('jogos', ['time1', 'time2', 'campeonato', 'data_do_jogo'], [jogo_do_dia['time1'], jogo_do_dia['time2'], campeonato_jogo, data_hora_jogo])
            if insert:
                inseriu = True
            else:
                inseriu = False
        if inseriu:
            db.faz_commit()
            print(f'Jogos do dia "{data_hora_jogo}" inserido com sucesso.')
        else:
            db.faz_rollback()
            print(f'Falha ao inserir jogos do dia {data_hora_jogo} no Banco de Dados')
    
    def atualiza_resultados_jogos_de_ontem_no_bd(self, jogos_de_ontem, campeonato_jogos, data_hora_jogos, resultado_jogos_de_ontem):
        '''
            Esta função atualiza a coluna "resultado" de cada jogo que foi jogado no dia anterior.
            :param jogos_do_dia: objeto contendo o nome dos dois times de cada jogo
            :param campeonato_jogos: array contendo o nome dos campeonatos de cada jogo
            :param data_hora_jogos: array contendo a data e hora que cada jogo ocorreu
            :param data_hora_jogos: array contendo o resultado de cada jogo que ocorreu no dia anterior.
        '''
        db = database.DatabaseManager()
        db.iniciar_transacao()
        for jogo_de_ontem, campeonato_jogo, data_hora_jogo, resultado_jogo in zip(jogos_de_ontem, campeonato_jogos, data_hora_jogos, resultado_jogos_de_ontem):
            update = db.realizar_update('jogos', f'resultado = "{resultado_jogo}"', f'data_do_jogo = "{data_hora_jogo}" AND time1 = "{jogo_de_ontem['time1']}" AND time2 = "{jogo_de_ontem['time2']}" and campeonato = "{campeonato_jogo}"')
            if update:
                atualizou = True
            else:
                atualizou = False
        if atualizou:
            db.faz_commit()
            print(f'Resultado dos jogos do dia "{data_hora_jogo}" atualizados com sucesso.')
        else:
            db.faz_rollback()
            print(f'Falha ao atualizar resultados dos jogos do dia "{data_hora_jogo}" no Banco de Dados')