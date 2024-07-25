import os
import signal
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import threading
import scraping
import pagamento

# carrega dotenv
load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=discord.Intents.all())
        
        self.cogslist = ["cogs.commands"]
    
    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        print(f'    Logado como {self.user.name}')
        print(f'    Bot ID: {self.user.id}')
        print(f'    Versão do Discord: {discord.__version__}')
        await self.tree.sync()

def signal_handler(sig, frame):
    print('Ctrl + C pressionado. Encerrando...')
    os._exit(0)
    
# importa token do .env e executa a aplicacao
TOKEN = os.getenv('DISCORD_TOKEN') 

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    scraping_thread = threading.Thread(target=scraping.WebScrapJogos().agenda_scraping)
    pagamento_thread = threading.Thread(target=pagamento.agenda_pagamento)

    scraping_thread.start()
    pagamento_thread.start()

    bot = Bot()
    bot.run(TOKEN)