from discord.ext import commands
from typing import List, Mapping, Optional
import discord


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        author: discord.User = self.context.author
        color = discord.Color.from_rgb(30, 99, 175)
        embed = discord.Embed(description='Here is a list of commands for Hayato.', color=color)
        for item in mapping.items():
            cmds: List[commands.Command] = await self.filter_commands(commands=item[1], sort=True)
            cmd_names = map(lambda x: '`' + x.name + '`', cmds)
            cmd_string = ' '.join(cmd_names)
            category_name: str
            if item[0] is not None:
                category_name = str(item[0].qualified_name)
            else:
                category_name = 'No Category'
            embed.add_field(name=category_name, value=cmd_string, inline=True)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text='Type h!help command for more info on a command.\nYou can also type h!help category for more info on a category.')
        await self.context.send(embed=embed)