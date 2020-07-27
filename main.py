import discord
import random
from datetime import datetime


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        # Add a series of games Hayato is going to play.
        self.trains = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5', 'Shinkansen E6']
        self.last_updated = datetime.now()
        self.pings = ['pong', 'pang', 'pung']

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

        if message.content == 'h!ping':
            await message.channel.send(random.choice(self.pings))

        if message.content.startswith('h!vowels'):
            user_input = message.content[9:]
            answer = self.count_vowels(user_input)
            await message.channel.send('There are ' + str(answer) + ' vowels in the input!')

        # Switch presence every hour
        if (datetime.now() - self.last_updated).seconds > 3600:
            await self.switch_presence()

    # Count vowels
    def count_vowels(self, string):
        count = 0
        for letter in string:
            if letter in 'aeiou':
                count += 1
        return count


client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
