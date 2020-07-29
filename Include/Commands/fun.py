import typing
from discord.ext import commands


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def fascinated(self, ctx: commands.Context, count: typing.Optional[int] = 0):
        result = ''
        if str(count) == '' or count == 0:
            result = 'https://cdn.discordapp.com/emojis/705279783340212265.gif'
        else:
            for i in range(0, count):
                result += '<a:KouFascinated:705279783340212265> '
        await ctx.send(result)


def setup(bot: commands.Bot):
    bot.add_cog(FunCog(bot))
