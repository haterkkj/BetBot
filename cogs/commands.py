import os
import database
import utils.paginator as paginator
import discord
import usuario
from discord.ext import commands
from discord import app_commands

OWNER_ID = os.getenv('OWNER_ID')
def cooldown_pra_todos_menos_owner(interact: discord.Interaction):
    if interact.user.id == OWNER_ID:
        return None
    return app_commands.Cooldown(1, 60.0)

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        database.criar_tabelas()

    @app_commands.command(name='apostar', description='Comando utilizado para apostar em um time.')
    @app_commands.choices(timevencedor=[
        app_commands.Choice(name='Time 1', value='time1'),
        app_commands.Choice(name='Time 2', value='time2'),
        app_commands.Choice(name='Empate', value='empate')
    ])
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def apostar(self, interaction: discord.Interaction, idjogo: int, valorapostado: float, timevencedor: app_commands.Choice[str]):
        '''
            Esta função é responsável por criar o comando de aposta que o usuário utilizara para apostar
            no bot.
            :param idjogo: ID do jogo, passado pelo usuário por meio de texto
            :param valorapostado: valor que o usuário deseja apostar, também passado pelo usuário
            :param timevencedor: palpite do usuário, 3 valores possiveis criados acima, são apresentados em forma de menu dropdown.
        '''
        apostou, mensagem = usuario.apostar(interaction.user.id, idjogo, valorapostado, timevencedor.value)
        if apostou:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)

class Cancelar(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='aposta', description='Comando utilizado para cancelar uma aposta que o usuário realizou.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def deletar_aposta_do_DB(self, interaction: discord.Interaction, aposta_id: int):
        '''
            Esta função é responsável por criar o comando de cancelar aposta que o usuário
            utilizará para cancelar uma aposta que ele tenha feito.
            Só é possível cancelar apostas feitas por você, antes de que o jogo tenha se iniciado.
            :param aposta_id: identificação (ID) da aposta que o usuário deseja cancelar.
        '''
        user = interaction.user
        deletou, mensagem = usuario.cancelar_aposta(user.id, aposta_id)
        if deletou:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)

class Visualizar(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name='apostas', description='Comando utilizado para visualizar apostas que o usuário realizou.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def listar_apostas_no_DB(self, interaction: discord.Interaction):
        '''
            Esta função é responsável por criar o comando "visualizar apostas", serve para que o usuário
            veja todas as apostas que ele já tenha realizado.
        '''
        user = interaction.user
        listou, mensagem = usuario.listar_apostas_do_usuario(user.id, interaction)
        if listou:
            await interaction.response.send_message(embed=mensagem.initial, view=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)
    
    @app_commands.command(name='jogos', description='Comando utilizado para listar jogos que vão ocorrer no dia e são possiveis de apostar')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def listar_jogos_do_dia(self, interaction: discord.Interaction):
        '''
            Esta função é responsável por criar o comando "visualizar jogos", serve para que o usuário
            veja todos os jogos que ainda ocorrerão no dia de hoje, sendo eles, os jogos que
            o usuário pode apostar.
        '''
        listou, mensagem = usuario.lista_jogos_do_dia()
        if listou:
            await interaction.response.send_message(embed=mensagem.initial, view=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)

        

class Saldo(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='consultar', description='Comando utilizado para verificar seu saldo.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def consultar_saldo_no_BD(self, interact:discord.Interaction):
        '''
            Esta função é responsável por criar o comando "saldo consultar", serve para que o usuário
            veja o saldo que possui em sua conta.
        '''
        user = interact.user
        consultou, mensagem, _ = usuario.consultar_saldo(user.id)
        if consultou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='depositar', description='Comando utilizado para adicionar dinheiro à sua conta.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def depositar(self, interact:discord.Interaction, valor: float):
        '''
            Esta função é responsável por criar o comando "saldo depositar", serve para que o usuário
            deposite um valor X em sua conta. Este valor é o que ele terá disponível para apostar.
            :param valor: valor tipo float com quantidade de dinheiro que usuário deseja depositar
        '''
        user = interact.user
        depositou, mensagem = usuario.adicionar_saldo(user.id, valor)
        if depositou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='sacar', description='Comando utilizado para adicionar sacar dinheiro de sua conta.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def sacar(self, interact:discord.Interaction, valor: float):
        '''
            Esta função é responsável por criar o comando "saldo sacar", serve para que o usuário
            saque um valor X de sua conta.
            :param valor: valor tipo float com quantidade de dinheiro que usuário deseja sacar
        '''
        user = interact.user
        sacou, mensagem = usuario.sacar_saldo(user.id, valor)
        if sacou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='extrato', description='Comando utilizado para verificar o extrato do seu saldo.')
    @app_commands.checks.dynamic_cooldown(cooldown_pra_todos_menos_owner)
    async def extrato(self, interact:discord.Interaction):
        '''
            Esta função é responsável por criar o comando "saldo extrato", serve para que o usuário
            veja todas as operações envolvendo dinheiro que já foram feitas na sua conta.
        '''
        user = interact.user
        consultou, mensagem = usuario.recuperar_extrato(user.id, interact)
        if consultou:
            await interact.response.send_message(embed=mensagem.initial, view=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Commands(bot))
    await bot.add_cog(Cancelar(bot))
    await bot.add_cog(Visualizar(bot))
    await bot.add_cog(Saldo(bot))