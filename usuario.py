import database
import utils.paginator as paginator
import discord
import datetime
import time
from zoneinfo import ZoneInfo

img = 'https://us.123rf.com/450wm/pixelliebe/pixelliebe2009/pixelliebe200900100/156071369-bola-de-futebol-bola-de-futebol-campo-est%C3%A1dio-%C3%ADcone-s%C3%ADmbolo-plano-design-vector.jpg'
nome_bot = 'BetBot'

def consultar_saldo(userid: int):
    '''
        Esta função faz um select na tabela 'usuario', recupera o saldo do usuário
        e informa para o mesmo qual valor ele tem em sua conta.
        :param userid: ID de usuário da pessoa que executou o comando
        :return: retorna um valor boolean para o caso da operação dar certo ou errado,
                 uma mensagem que será enviada para o usuário informando o saldo ou o erro,
                 e caso a operação for bem sucedida, também é retornado o valor do saldo do usuário
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    select = db.realizar_select('usuario', '*', f'id = {userid}')
    if select:
        select = db.realizar_select('usuario', ['saldo'], f'id = {userid}')
        if select:
            usuario = select [0]
            mensagem = discord.Embed(title='Carteira', description=f'Você possui `R$ {usuario['saldo']}` em sua carteira.', color=discord.Color.brand_green())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_commit()
            return True, mensagem, float(usuario['saldo'])
        else:
            print(f'Houve um erro ao consultar o saldo do usuário {userid}.')
            mensagem = discord.Embed(title='Erro ao consultar carteira', description=f'Enfrentamos um erro ao consultar o saldo do usuário `{userid}`. Contate um administrador.', color=discord.Color.brand_red())
            db.faz_rollback()
            return False, mensagem, None
    else:
        print(f'Não encontramos o usuario {userid} no Banco de Dados.')
        mensagem = discord.Embed(title='Quem é você?', description=f'Não foi possível encontrar o usuário `{userid}` no sistema.\nLembre-se que seu cadastro é feito automáticamente ao realizar um depósito.', color=discord.Color.brand_green())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem, None

def adicionar_saldo(userid: int, valor: float):
    '''
        Esta função recebe o valor que o usuário deseja depositar em sua conta e
        faz o insert ou update no banco de dados do valor somando o valor antigo que é recuperado
        por um select ao valor que o usuário está inserindo agora.
        Caso o usuário nunca tiver feito um depósito o usuário é inserido no sistema automáticamente.
        A ação também é inserida na tabela 'transacoes' do BD.
        :param userid: ID de usuário da pessoa que executou o comando
        :param valor: valor que o usuário deseja depositar em sua conta
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem de sucesso ou erro para que o usuário saiba o que ocorreu.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    now = database.retorna_data_hora_no_formato_do_bd()

    if valor < 10.00:
        mensagem = discord.Embed(title='Valor insuficiente', description=f'O depósito mínimo é de `R$ 10,00`.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        return False, mensagem
    else:
        select = db.realizar_select('usuario', '*', f'id = {userid}')
        if select:
            usuario = select[0]
            saldo_atualizado = float(usuario['saldo']) + valor
            insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [userid, 'Depósito', now, usuario['saldo'], saldo_atualizado])
            if not insert:
                mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não conseguimos atualizar seu LOG.\nContate um administrador do sistema.\nErro CA003', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
            update = db.realizar_update('usuario', f'saldo = {saldo_atualizado}', f'id = {userid}')
            if update:
                print(f'O usuário {userid} adicionou R$ {valor} à conta.')
                mensagem = discord.Embed(title='Deposito realizado com sucesso!', description=f'O valor `R$ {valor}` foi adicionado com sucesso em sua carteira.', color=discord.Color.brand_green())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_commit()
                return True, mensagem  
            else:
                mensagem = discord.Embed(title='Erro ao depositar', description=f'Houve um erro ao adicionar o saldo em sua carteira. Contate um administrador.', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
        else:
            insert = db.realizar_insert('usuario', ['id', 'saldo'], [userid, 0])
            if insert:
                print(f'Usuario {userid} inserido no sistema com sucesso.')
                update = db.realizar_update('usuario', f'saldo = {valor}', f'id = {userid}')
                if update:
                    insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [userid, 'Depósito', now, 0, valor])
                    if not insert:
                        mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não conseguimos atualizar seu LOG.\nContate um administrador do sistema.\nErro CA003', color=discord.Color.brand_red())
                        mensagem.set_author(name=nome_bot, icon_url=img)
                        db.faz_rollback()
                        return False, mensagem
                    print(f'O usuário {userid} adicionou R$ {valor} à conta.')
                    mensagem = discord.Embed(title='Deposito realizado com sucesso!', description=f'O valor `R$ {valor}` foi adicionado com sucesso em sua carteira.', color=discord.Color.brand_green())
                    mensagem.set_author(name=nome_bot, icon_url=img)
                    db.faz_commit()
                    return True, mensagem
                else:
                    mensagem = discord.Embed(title='Erro ao depositar', description=f'Houve um erro ao adicionar o saldo em sua carteira. Contate um administrador.', color=discord.Color.brand_red())
                    mensagem.set_author(name=nome_bot, icon_url=img)
                    db.faz_rollback()
                    return False, mensagem
            else:
                mensagem = discord.Embed(title='Erro ao cadastrar usuário', description=f'Houve um erro ao cadastrar o usuario `{userid}` no sistema. Contate um administrador.', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem

def sacar_saldo(userid:int, valor: float):
    '''
        Esta função recebe o valor que o usuário deseja sacar, recupera o valor que ele possui em sua conta
        e caso haver a quatia suficiente, o saldo do usuário é atualizado com o novo saldo.
        A ação também é inserida na tabela 'transacoes' do BD.
        :param userid: ID de usuário da pessoa que executou o comando
        :param valor: valor que o usuário deseja retirar de sua conta
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem de sucesso ou erro para que o usuário saiba o que ocorreu.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    now = database.retorna_data_hora_no_formato_do_bd()
    select = db.realizar_select('usuario', '*', f'id = {userid}')
    if select:
        usuario = select[0]
        if usuario['saldo'] < valor:
            mensagem = discord.Embed(title='Erro ao realizar saque!', description=f'Não é possível sacar uma quantia maior do que existe em sua carteira.\nCorrija os valores e tente novamente.', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        elif valor < 10.00:
            mensagem = discord.Embed(title='Erro ao realizar saque!', description=f'O valor mínimo de saque é `R$ 10,00`.\nCorrija os valores e tente novamente.', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        else: 
            saldo_atualizado = float(usuario['saldo']) - valor
            insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [userid, 'Saque', now, usuario['saldo'], saldo_atualizado])
            if not insert:
                mensagem = discord.Embed(title='Erro ao sacar', description=f'Houve um erro ao concluir o saque, foi impossível atualizar o seu LOG. Tente novamente e verifique atentamente os valores.\nCaso persistir contate um administrador.', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
            update = db.realizar_update('usuario', f'saldo = {saldo_atualizado}', f'id = {userid}')
            if update:
                print(f'O usuário {userid} sacou R$ {valor} de sua conta.')
                mensagem = discord.Embed(title='Saque realizado com sucesso!', description=f'O saque no valor de `R$ {valor}` foi realizado com sucesso.\nEsperamos ter você mais vezes conosco!', color=discord.Color.brand_green())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_commit()
                return True, mensagem  
            else:
                mensagem = discord.Embed(title='Erro ao sacar', description=f'Houve um erro ao efetuar o saque, tente novamente verificando atentamente os valores.\nCaso persistir contate um administrador.', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
    else:
        mensagem = discord.Embed(title='Usuário não existe no sistema', description=f'Aparentemente você ainda não foi cadastrado em nosso sistema.\nCaso deseje criar uma conta, ela é criada automaticamente ao realizar seu primeiro depósito.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
def recuperar_extrato(userid: int, interaction: discord.Interaction):
    '''
        Esta função é responsável por mostrar o extrato de todas as operações envolvendo o saldo
        do usuário que foram realizadas desde o primeiro depósito até o momento de execução da função.
        :param userid: ID de usuário da pessoa que executou o comando
        :param interaction: interação do usuário com a aplicação no discord.
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem de sucesso ou erro para que o usuário saiba o que ocorreu.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    select = db.realizar_select('transacoes', '*', f'user_id = {userid}')
    embeds = []
    lista_operacoes = []
    if select:
        cont = 0
        operacao = ''
        qtd_rows = len(select)
        for row in select:
            operacao += f'**ID Transação:** `{row['id']}` | **Tipo:** `{row['tipo_transacao']}` | **Saldo Anterior:** `{row['saldo_antes']}` | **Saldo Atualizado:** `{row['saldo_depois']}` | **Data da operação:** `{row['data_da_transacao']}`\n\n'
            cont += 1
            qtd_rows -= 1
            if cont >= 10 or qtd_rows == 0:
                lista_operacoes.append(operacao)
                operacao = ''
                cont = 0
        for operacao in lista_operacoes:
            embed = discord.Embed(title=f'Extrato de {interaction.user.name}', description=operacao, color=discord.Color.brand_green())
            embed.set_author(name=nome_bot, icon_url=img)
            embeds.append(embed)
        view = paginator.PaginatorView(embeds)
        db.faz_commit()
        return True, view
    else:
        mensagem = discord.Embed(title='Erro ao consultar extrato', description=f'Enfrentamos um erro ao consultar seu extrato.\nCaso você já for um usuário do nosso bot, contate um administrador.\nCaso for sua primeira vez utilizando nossos serviços, só será possível consultar seu extrato após ser cadastrado depositando com o comando `/saldo depositar`.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem

def apostar(userid: int, jogoid: int, valor: float, time: str):
    '''
        Esta função recebe o ID do usuário, o valor que ele deseja apostar, o jogo em que
        ele deseja apostar e o palpite dele sobre o jogo.
        A ação também é inserida na tabela 'transacoes' do BD.
        :param userid: ID de usuário da pessoa que executou o comando
        :param jogoid: ID do jogo informado pelo usuário
        :param valor: valor informado pelo usuário
        :param time: palpite do usuário sobre o jogo.
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem de sucesso ou erro para que o usuário saiba o que ocorreu.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    now = database.retorna_data_hora_no_formato_do_bd()
    
    if valor < 1:
        mensagem = discord.Embed(title='Valor invalido', description=f'Não é possível fazer apostas menores do que `R$ 1,00`.\nVerifique os valores e tente novamente.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        return False, mensagem
    
    select = db.realizar_select('usuario', '*', f'id = {userid}')
    if not select:
        mensagem = discord.Embed(title='Usuário não existe no sistema', description=f'Aparentemente você ainda não foi cadastrado em nosso sistema.\nCaso deseje criar uma conta, ela é criada automaticamente ao realizar seu primeiro depósito.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    select = db.realizar_select('jogos', ['id'], f'id = {jogoid}')
    if not select:
        mensagem = discord.Embed(title='Erro na aposta', description=f'Você está tentando apostar em um jogo inexistente.\nVerifique o ID do jogo e tente novamente.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    select = db.realizar_select('jogos', ['id'], f'id = {jogoid} and data_do_jogo >= "{now}"')
    if not select:
        mensagem = discord.Embed(title='Erro na aposta', description=f'Você está tentando apostar em um jogo que já aconteceu no passado.\nVeja os jogos apostáveis usando o comando `/jogos-do-dia`.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    select = db.realizar_select('aposta', '*', f'jogo_id = {jogoid} and user_id = {userid}')
    if select:
        mensagem = discord.Embed(title='Você já realizou esta aposta', description=f'Você já realizou uma aposta nesse jogo.\nCaso queira fazer outra aposta no mesmo jogo, cancele a anterior usando o comando `/placeholder`.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    consultou, _, saldo_usuario = consultar_saldo(userid)
    if consultou:
        if saldo_usuario < valor:
            mensagem = discord.Embed(title='Saldo insuficiente!', description=f'Você não tem saldo o suficiente para realizar esta aposta.\nVerifique os valores e tente novamente.', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        else:
            saldo_atualizado = saldo_usuario - valor
            insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [userid, 'Aposta', now, saldo_usuario, saldo_atualizado])
            if not insert:
                mensagem = discord.Embed(title='Erro ao apostar', description=f'Erro ao atualizar seu LOG durante a operação de aposta. Tente novamente e verifique atentamente os valores.\nCaso persistir o erro, contate um administrador.', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
            update = db.realizar_update('usuario', f'saldo = {saldo_atualizado}', f'id = {userid}')
            if update:
                insert = db.realizar_insert('aposta', ['user_id', 'jogo_id', 'palpite', 'valor_aposta', 'data_da_aposta', 'situacao'], [userid, jogoid, time, valor, now, 'Esperando'])
                if insert:
                    select = db.realizar_select('aposta', ['id'], f"user_id = {userid} and valor_aposta = {valor} and data_da_aposta = '{now}'", None, 'id DESC')
                    if select:
                        aposta = select[0]
                        mensagem = discord.Embed(title='Aposta criada com sucesso!', description=f'A aposta foi adicionada com sucesso ao sistema.\n`ID da Aposta: {aposta['id']}`', color=discord.Color.brand_green())
                        mensagem.set_author(name=nome_bot, icon_url=img)
                        db.faz_commit()
                        return True, mensagem
                    else: 
                        mensagem = discord.Embed(title='Erro ao selecionar a aposta!', description=f'A aposta foi adicionada com sucesso ao sistema. Porém enfrentamos problemas ao recuperar o ID da mesma.\n Contate um administrador.', color=discord.Color.brand_red())
                        mensagem.set_author(name=nome_bot, icon_url=img)
                        db.faz_rollback()
                        return False, mensagem
                else:
                    mensagem = discord.Embed(title='Aposta cancelada', description=f'Não foi possível realizar a aposta.\nTente novamente ou contate um administrador do sistema.', color=discord.Color.brand_red())
                    mensagem.set_author(name=nome_bot, icon_url=img)
                    db.faz_rollback()
                    return False, mensagem
            else: 
                mensagem = discord.Embed(title='Erro ao atualizar saldo', description=f'Não conseguimos sincronizar seu saldo após ser feita a aposta.\nContate um administrador do sistema. Código de erro `ap-001`', color=discord.Color.brand_red())
                mensagem.set_author(name=nome_bot, icon_url=img)
                db.faz_rollback()
                return False, mensagem
    else:
        mensagem = discord.Embed(title='Erro ao atualizar saldo', description=f'Não conseguimos sincronizar seu saldo após ser feita a aposta.\nContate um administrador do sistema. Código de erro `ap-002`', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
def cancelar_aposta(userid, apostaid):
    '''
        Esta função recebe do usuário o ID da aposta que ele deseja cancelar e
        caso for possível, a mesma é apagada do sistema e o saldo é devolvido a sua conta.
        A ação também é inserida na tabela 'transacoes' do BD.
        :param userid: ID de usuário da pessoa que executou o comando
        :param apostaid: ID da aposta que o usuário deseja cancelar
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem de sucesso ou erro para que o usuário saiba o que ocorreu.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    now = database.retorna_data_hora_no_formato_do_bd()

    select = db.realizar_select('aposta', ['id', 'user_id', 'jogo_id', 'valor_aposta'], f'id = {apostaid} and user_id = {userid}')
    if not select:
        mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Você está tentando cancelar uma aposta que não é sua ou não existe.\nSó é possível cancelar apostas que **VOCÊ** fez e antes que os jogos sejam iniciados.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    select = select[0]
    jogoid = select['jogo_id']
    valor_aposta = select['valor_aposta']
    select = db.realizar_select('jogos', ['data_do_jogo'], f'id = {jogoid} and data_do_jogo > "{now}"')
    if not select:
        mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Este jogo já foi iniciado.\nNão é possível cancelar uma aposta após o jogo ser iniciado.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
    delete = db.realizar_delete('aposta', f'id = {apostaid}')
    if delete:
        select = db.realizar_select('usuario', ['saldo'], f'id = {userid}')
        if not select:
            mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não conseguimos devolver seu saldo.\nContate um administrador do sistema.\nErro CA001', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        
        select = select[0]
        saldo_atualizado = select['saldo'] + valor_aposta
        update = db.realizar_update('usuario', f'saldo = {saldo_atualizado}', f'id = {userid}')
        if not update:
            mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não conseguimos devolver seu saldo.\nContate um administrador do sistema.\nErro CA002', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        
        insert = db.realizar_insert('transacoes', ['user_id', 'tipo_transacao', 'data_da_transacao', 'saldo_antes', 'saldo_depois'], [userid, 'Aposta Cancelada', now, select['saldo'], saldo_atualizado])
        if not insert:
            mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não conseguimos atualizar seu LOG.\nContate um administrador do sistema.\nErro CA003', color=discord.Color.brand_red())
            mensagem.set_author(name=nome_bot, icon_url=img)
            db.faz_rollback()
            return False, mensagem
        
        mensagem = discord.Embed(title='Aposta cancelada com sucesso', description=f'A aposta de ID `{apostaid}` foi cancelada com sucesso.', color=discord.Color.brand_green())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_commit()
        return True, mensagem
    else:
        mensagem = discord.Embed(title='Erro ao cancelar aposta', description='Não foi possível DELETAR sua aposta do sistema. Se o erro persistir, contate um administrador do sistema.', color=discord.Color.brand_red())
        mensagem.set_author(name=nome_bot, icon_url=img)
        db.faz_rollback()
        return False, mensagem
    
def listar_apostas_do_usuario(userid: int, interaction: discord.Interaction):
    '''
        Esta função é responsável por mostrar todas as apostas que o usuario já realizou.
        :param userid: ID de usuário da pessoa que executou o comando
        :param interaction: interação do usuário com a aplicação no discord.
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem contendo todas as apostas já realizadas ou mensagem de erro.
    '''
    db = database.DatabaseManager()
    db.iniciar_transacao()
    embeds = []
    select = db.realizar_select('aposta', ['aposta.id', 'aposta.jogo_id', 'jogos.time1', 'jogos.time2', 'jogos.campeonato', 'jogos.data_do_jogo', 'aposta.palpite', ' aposta.valor_aposta', 'aposta.data_da_aposta', 'aposta.situacao'], f'user_id = {userid}', 'inner join jogos on aposta.jogo_id = jogos.id', 'aposta.id ASC')
    if select:
        for row in select:
            embed = discord.Embed(title=f'Apostas de {interaction.user.name}', color=discord.Color.brand_green())
            if row['palpite'] == "empate":
                palpite = "Empate."
            else:
                palpite = f'{row[row['palpite']]} vence.'
            embed.add_field(name=f'Aposta n° {row['id']}:', value=f'\n\n **⭢ 💸 Valor da aposta:** `R$ {row['valor_aposta']}`\n\n **⭢ 📅 Data da Aposta:** `{row['data_da_aposta']}`\n\n **⭢ ⚽ Jogo Apostado: **`{row['time1']} X {row['time2']} | {row['campeonato']}`\n\n **⭢ 📅 Data do Jogo:** `{row['data_do_jogo']}`\n\n **⭢ 🏆 Palpite:** `{palpite}`\n\n **⭢ 📋 Situacao:** `{row['situacao']}`')
            embed.set_author(name=nome_bot, icon_url=img)
            embeds.append(embed)
        view = paginator.PaginatorView(embeds)
        db.faz_commit()
        return True, view
    else:
        embed = discord.Embed(title='Erro ao visualizar apostas', description='Aparentemente você ainda não tem nenhuma aposta.\nApós apostar, você poderá ver as apostas realizadas aqui.\n\nCaso você já tenha apostado e o erro segue ocorrendo, contate um administrador.', color=discord.Color.brand_red())
        db.faz_rollback()
        return False, embed
    
def lista_jogos_do_dia():
    '''
        Esta função realiza um select dos jogos que irão acontecer hoje e os mostra para o usuário.
        :return: valor boolean para o caso de a operação dar certo ou errado e
                 mensagem contendo todos os jogos do dia ou mensagem de erro.
    '''
    embeds = []
    now = database.retorna_data_hora_no_formato_do_bd()
    db = database.DatabaseManager()
    db.iniciar_transacao()
    select = db.realizar_select('jogos', '*', f'data_do_jogo >= "{now}"')
    if select:
        embed = discord.Embed(title='Jogos do dia', color=discord.Color.brand_green())
        qtd_fields = 0
        rows_faltantes = len(select)
        for row in select:
            embed.add_field(name=f'{row['time1']} X {row['time2']}', value=f'🏟️ ***{row['campeonato']}***\n🆔 ID do Jogo: `{row['id']}`\n1️⃣ Time 1: `{row['time1']}`\n2️⃣ Time 2: `{row['time2']}`\n📅 Data: `{row['data_do_jogo']}`', inline= False)
            qtd_fields += 1
            rows_faltantes -= 1
            if qtd_fields >= 4 or rows_faltantes == 0:
                embed.set_author(name=nome_bot, icon_url=img)
                embeds.append(embed)
                embed = discord.Embed(title='Jogos do dia', color=discord.Color.brand_green())
                qtd_fields = 0
        view = paginator.PaginatorView(embeds)
        db.faz_commit()
        return True, view
    else:
        mensagem = discord.Embed(title='Erro ao consultar jogos do dia', description='Não conseguimos consultar os jogos de hoje.\nContate um administrador do sistema.', color=discord.Color.brand_red())
        db.faz_rollback()
        return False, mensagem