from discord.ext import commands
import json
import random


class ShinkansenCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        with open('Storage/trains.json', 'r', encoding='utf-8') as file:
            raw_trains = file.read()
            self.trains = json.loads(raw_trains)

    @commands.command()
    async def train(self, ctx: commands.Context):
        train = random.choice(self.trains)
        await ctx.send('I got ' + train['name'] + '!')
        await ctx.send(train['link'])


def setup(bot: commands.Bot):
    bot.add_cog(ShinkansenCog(bot))