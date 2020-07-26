import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        game = discord.Game("Shinkansen E5")
        await client.change_presence(status=discord.Status.online, activity=game)        

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')