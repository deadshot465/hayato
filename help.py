from discord.ext import commands
from typing import List, Mapping, Optional, Set
import discord


class Help(commands.HelpCommand):
    def __init__(self, command_attrs: dict):
        super().__init__(command_attrs=command_attrs)
        self.color = discord.Color.from_rgb(30, 99, 175)

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        author: discord.User = self.context.author
        embed = discord.Embed(description='Here is a list of commands for Hayato.', color=self.color)
        for item in mapping.items():
            cmds: List[commands.Command] = await self.filter_commands(commands=item[1], sort=True)
            cmds_dedup: Set[commands.Command] = set(cmds)
            cmd_names = map(lambda x: '`' + x.name + '`', cmds_dedup)
            cmd_string = ' '.join(cmd_names)
            category_name: str
            if item[0] is not None:
                category_name = str(item[0].qualified_name)
            else:
                category_name = 'No Category'
            embed.add_field(name=category_name, value=cmd_string, inline=True)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text='Type h!help <command> for more info on a command.\nYou can also type h!help <category> for more info on a category.')
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        cmds: List[commands.Command] = await self.filter_commands(commands=cog.get_commands(), sort=True)
        author: discord.User = self.context.author
        embed = discord.Embed(description='Here is a list of commands for `{}`.'.format(cog.qualified_name), color=self.color, title=cog.qualified_name)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text='Type h!help <command> for more info on a command.')
        for cmd in cmds:
            embed.add_field(name=cmd.name, value=cmd.description, inline=False)
        await self.context.send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        author: discord.User = self.context.author
        embed = discord.Embed(description=command.help,
                              color=self.color, title=command.name)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        if command.aliases is not None and len(command.aliases) > 0:
            aliases = map(lambda x: '`{}`'.format(x), command.aliases)
            embed.add_field(name='Aliases', value=' '.join(aliases), inline=False)
        await self.context.send(embed=embed)
