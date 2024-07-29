import database
import schedule
import datetime
import time
from zoneinfo import ZoneInfo

def agenda_pagamento():
    '''
        Esta função é responsável por agendar o pagamento das
        apostas do dia anterior, definindo a hora em que o programa
        deve executar as funções da rotina.
    '''
    schedule.every().day.at('04:00').do(pagar_apostas)
    print('Rotina de pagamento agendada.')
    while True:
        schedule.run_pending()
        time.sleep(90)

def pagar_apostas():
    '''
        Esta função é responsável por selecionar todas as apostas feitas e jogos realizados no dia anterior
        e devolve o valor da aposta multiplicado pela odd do jogo (sistema de odd ainda não implementado, por padrão é pago 2 vezes o valor apostado)
        caso o palpite e o resultado do jogo forem iguais.
        :return: valor boolean falso para o caso de não haverem jogos constando no dia anterior ou apostas a serem pagas
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    
    hoje = datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
    ontem = hoje - datetime.timedelta(days=1)
    hoje = hoje.strftime('%Y-%m-%d %H:%M:%S')
    ontem = ontem.strftime('%Y-%m-%d %H:%M:%S')
    
    jogos_de_ontem = db.realizar_select('jogos', ['id', 'resultado'], f'data_do_jogo >= "{ontem}" and data_do_jogo <= "{hoje}"')
    apostas_de_ontem = db.realizar_select('aposta', ['id', 'jogo_id', 'palpite', 'valor_aposta', 'user_id', 'situacao'], f'data_da_aposta >= "{ontem}" and data_da_aposta < "{hoje}" and situacao = "Esperando"')

    if not apostas_de_ontem or not jogos_de_ontem:
        print("Não há jogos ou apostas a serem pagas no sistema.")
        db.faz_rollback()        
        return False
    else:
        db.faz_commit()

    for aposta in apostas_de_ontem:
        db.iniciar_transacao()
        resultado_jogo = ''
        for jogo in jogos_de_ontem:
            if jogo['id'] == aposta['jogo_id']:
                resultado_jogo = jogo['resultado']
                break
        if resultado_jogo == aposta['palpite']:     
            valor_pago = float(aposta['valor_aposta']) * 2 
            select = db.realizar_select('usuario', ['saldo'], f'id = {aposta['user_id']}')
            if select:
                select = select[0]
                saldo_anterior = float(select['saldo'])
                novo_saldo = valor_pago + saldo_anterior
                insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [aposta['user_id'], 'Pagamento Aposta', database.retorna_data_hora_no_formato_do_bd(), saldo_anterior, novo_saldo])
                if insert:
                    update_aposta = db.realizar_update('aposta', 'situacao = "Aposta Paga"', f'id = {aposta['id']}')
                    update_usuario = db.realizar_update('usuario', f'saldo = {novo_saldo}', f'id = {aposta['user_id']}')
                    if update_aposta and update_usuario :
                        print(f'Aposta de ID <{aposta['id']}> paga com sucesso.')
                        db.faz_commit()
                    else:
                        print(f'Houve um erro ao pagar a aposta <{aposta['id']}>.')
                        db.faz_rollback()
                else:
                    print(f'Houve um erro ao atualizar extrato do usuário <{aposta['user_id']}> durante a aposta <{aposta['id']}>')
                    db.faz_rollback()
            else:
                print(f'Não foi possível visualizar o saldo do usuário <{aposta['user_id']}>')
                db.faz_rollback()
        else:
            update = db.realizar_update('aposta', 'situacao = "Aposta Perdida"', f'id = {aposta['id']}')
            if update:
                print(f'Situação da aposta <{aposta['id']}> atualizada com sucesso. Status: Perdido.')
                db.faz_commit()
            else:
                print(f'Houve um erro ao atualizar situação da aposta <{aposta['id']}>. Status: Aposta perdida.')
                db.faz_rollback()