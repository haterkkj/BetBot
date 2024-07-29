import discord
from typing import List
from collections import deque

class PaginatorView(discord.ui.View):
    def __init__(
            self,
            embeds: List[discord.Embed]
    ) -> None:
        super().__init__(timeout=30)

        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1

        self._queue[0].set_footer(text=f'Página {self._current_page} de {self._len}')
        self.children[0].style = discord.ButtonStyle.green
        self.children[1].style = discord.ButtonStyle.green

    async def atualiza_footer(self, interaction: discord.Interaction, botaopressionado: str) -> None:
        '''
            Função responsável por atualizar footer do embed com a devida página em que
            se encontra.
            :param botaopressionado: recebe um valor contendo a informação de qual botão foi pressionado
        '''
        if botaopressionado == 'proximo':
            self._current_page += 1
        elif botaopressionado == 'anterior':
            self._current_page -= 1

        if self._current_page > self._len:
            self._current_page = 1
        elif self._current_page < 1:
            self._current_page = self._len

        for i in self._queue:
            i.set_footer(text=f'Página {self._current_page} de {self._len}')

    @discord.ui.button(label='<')
    async def anterior(self, interaction:discord.Interaction, _):
        '''
            Função responsável por criar o botão "anterior" e sua funcionalidade.
            Caso o botão for pressionado, a mensagem será atualizada com o embed anterior ao
            que estava sendo mostrado no momento.
        '''
        self._queue.rotate(1)
        embed = self._queue[0]
        await self.atualiza_footer(interaction, 'anterior')
        await interaction.response.edit_message(embed=embed)
        

    @discord.ui.button(label='>')
    async def proximo(self, interaction:discord.Interaction, _):
        '''
            Função responsável por criar o botão "próximo" e sua funcionalidade.
            Caso o botão for pressionado, a mensagem será atualizada com o próximo embed
            em relação ao que estava sendo mostrado.
        '''
        self._queue.rotate(-1)
        embed = self._queue[0]
        await self.atualiza_footer(interaction, 'proximo')
        await interaction.response.edit_message(embed=embed)
    

    @property
    def initial(self) -> discord.Embed:
        return self._initial
