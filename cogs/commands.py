import database
import paginator
import discord
import usuario
from discord.ext import commands
from discord import app_commands

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
    async def apostar(self, interaction: discord.Interaction, idjogo: int, valorapostado: float, timevencedor: app_commands.Choice[str]):
        apostou, mensagem = usuario.apostar(interaction.user.id, idjogo, valorapostado, timevencedor.value)
        if apostou:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)

class Cancelar(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='aposta', description='Comando utilizado para cancelar uma aposta que o usuário realizou.')
    async def deletar_aposta_do_DB(self, interaction: discord.Interaction, aposta_id: int):
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
    async def listar_apostas_no_DB(self, interaction: discord.Interaction):
        user = interaction.user
        listou, mensagem = usuario.listar_apostas_do_usuario(user.id, interaction)
        if listou:
            await interaction.response.send_message(embed=mensagem.initial, view=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)
    
    @app_commands.command(name='jogos', description='Comando utilizado para listar jogos que vão ocorrer no dia e são possiveis de apostar')
    async def listar_jogos_do_dia(self, interaction: discord.Interaction):
        listou, mensagem = usuario.lista_jogos_do_dia()
        if listou:
            await interaction.response.send_message(embed=mensagem.initial, view=mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mensagem, ephemeral=True)

class Saldo(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='consultar', description='Comando utilizado para verificar seu saldo.')
    async def consultar_saldo_no_BD(self, interact:discord.Interaction):
        user = interact.user
        consultou, mensagem, _ = usuario.consultar_saldo(user.id)
        if consultou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='depositar', description='Comando utilizado para adicionar dinheiro à sua conta.')
    async def depositar(self, interact:discord.Interaction, valor: float):
        user = interact.user
        depositou, mensagem = usuario.adicionar_saldo(user.id, valor)
        if depositou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='sacar', description='Comando utilizado para adicionar sacar dinheiro de sua conta.')
    async def sacar(self, interact:discord.Interaction, valor: float):
        user = interact.user
        sacou, mensagem = usuario.sacar_saldo(user.id, valor)
        if sacou:
            await interact.response.send_message(embed=mensagem, ephemeral=True)
        else:
            await interact.response.send_message(embed=mensagem, ephemeral=True)

    @app_commands.command(name='extrato', description='Comando utilizado para verificar o extrato do seu saldo.')
    async def extrato(self, interact:discord.Interaction):
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