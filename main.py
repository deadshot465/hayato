import discord
import random
from datetime import datetime


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        # Add a series of games Hayato is going to play.
        self.trains = ['Shinkansen E5', 'Shinkansen N700', 'Shinkansen L0', 'JR East KiHa 100', 'Shinkansen H5', 'Shinkansen E6', 'Shinkansen E7']
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
        
        if message.content.startswith('h!dashsep'):
            user_input = message.content[10:]
            answer = self.dash_separator(user_input)
            await message.channel.send(str(answer))
            
        if message.content.startswith('h!cvt f c'):
            user_input = message.content[10:]
            answer = self.cvt_f_c(user_input)
            await message.channel.send(str(user_input) + '¢K' + ' is equal to ' + 'answer' + '¢J.')  
            
        if message.content.startswith('h!cvt c f'):
            user_input = message.content[10:]
            answer = self.cvt_c_f(user_input)
            await message.channel.send(str(user_input) + '¢J' + ' is equal to ' + 'answer' + '¢K.')  
            
        # Switch presence every hour
        if (datetime.now() - self.last_updated).seconds > 3600:
            await self.switch_presence()

    # Count vowels
    def count_vowels(self, string):
        count = 0
        for letter in string:
            if letter in 'AEIOUaeiou':
                count += 1
        return count
    
    # Dash separator
    def dash_separator(string):
        '''(str) -> str
        Returns a string the separates each letter of the input string with a dash.
        
        >>> dash_separator('hello')
        h-e-l-l-o
        >>> Kirito
        K-i-r-i-t-o
        '''
        result = ''
        i = 0
        while i < len(string) - 1:
            result = result + string[i] + '-'
            i += 1
        result += string[i]
        return result
    
    # Convert ¢K to ¢J
    def cvt_f_c(fahrenheit):
        '''(float) -> float
        Return the temperature in celsius.
        '''
        celsius = (fahrenheit - 32) * 5 / 9
        return celsius
    
     # Convert ¢J to ¢K
    def cvt_c_f(celsius):
        '''(float) -> float
        Return the temperature in Fahrenheit.
        '''
        fahrenheit = celsius * 9 / 5 + 32
        return fahrenheit    
    
client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
