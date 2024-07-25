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
        self._queue.rotate(1)
        embed = self._queue[0]
        await self.atualiza_footer(interaction, 'anterior')
        await interaction.response.edit_message(embed=embed)
        

    @discord.ui.button(label='>')
    async def proximo(self, interaction:discord.Interaction, _):
        self._queue.rotate(-1)
        embed = self._queue[0]
        await self.atualiza_footer(interaction, 'proximo')
        await interaction.response.edit_message(embed=embed)
    

    @property
    def initial(self) -> discord.Embed:
        return self._initial
