import discord
import random
from datetime import datetime


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        # Add a series of games Hayato is going to play.
        self.trains = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5', 'Shinkansen E6']
        self.last_updated = datetime.now()

    # This function will switch Hayato's presence.
    async def switch_presence(self):
        game = discord.Game(random.choice(self.trains))
        await client.change_presence(status=discord.Status.online, activity=game)

    async def on_ready(self):
        print('Logged on as', self.user)
        await self.switch_presence()

    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

        # Switch presence every hour
        if (datetime.now() - self.last_updated).seconds > 3600:
            await self.switch_presence()


client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
