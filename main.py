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
            await message.channel.send(str(user_input) + '\u2109' + ' is equal to ' + str(answer) + '\u2103!')
            
        if message.content.startswith('h!cvt c f'):
            user_input = message.content[10:]
            answer = self.cvt_c_f(user_input)
            await message.channel.send(str(user_input) + '\u2103' + ' is equal to ' + str(answer) + '\u2109!')
        
        if message.content.startswith('h!cvt lbs kg'):
            user_input = message.content[13:]
            answer = self.cvt_lb_kg(user_input)
            await message.channel.send(str(user_input) + 'lbs' + ' is equal to ' + str(answer) + 'kg!') 
        
        if message.content.startswith('h!cvt kg lbs'):
            user_input = message.content[13:]
            answer = self.cvt_kg_lb(user_input)
            await message.channel.send(str(user_input) + 'kg' + ' is equal to ' + str(answer) + 'lbs!')
            
        if message.content.startswith('h!pick'):
            user_input = message.content[7:]
            answer = self.pick(user_input)
            await message.channel.send(answer)            
            
        # Switch presence every hour
        if (datetime.now() - self.last_updated).seconds > 3600:
            await self.switch_presence()
            self.last_updated = datetime.now()

    # Count vowels
    def count_vowels(self, string):
        count = 0
        for letter in string:
            if letter in 'AEIOUaeiou':
                count += 1
        return count
    
    # Dash separator
    def dash_separator(self, string):
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
    
    # Convert fahrenheit to celsius
    def cvt_f_c(self, fahrenheit):
        '''(float) -> float
        Return the temperature in celsius.
        '''
        celsius = (float(fahrenheit) - 32) * 5 / 9
        return celsius
    
    # Convert celsius to fahrenheit
    def cvt_c_f(self, celsius):
        '''(float) -> float
        Return the temperature in Fahrenheit.
        '''
        fahrenheit = float(celsius) * 9 / 5 + 32
        return fahrenheit  
    
    def cvt_lb_kg(self, lbs):
        kg = float(lbs) / 2.2
        return kg
    
    def cvt_kg_lb(self, kg):
        lb = float(kg) * 2.2
        return lb
    
    def pick(self, all_choices):
        '''
        Input several choices that split with "," and Hayato will help you choose one.
        '''
        error = False
        # Separate the choices into a list
        all_choices = all_choices.split(",")
        # For each choice remove the spaces
        for index in range(0, len(all_choices)):
            choice = all_choices[index].strip(" ")
            # If someone tries to fool Hayato, it is impossible
            if choice == "":
                error = True
                break        
            # Replace the choice with the no-blank-space one
            all_choices[index] = choice
        # Pick a random choice from the list
        hayatochoice = random.choice(all_choices)
        # return the choice
        if error == True:
            return "Are you trying to fool me?"
        else:
            return "I pick **" + hayatochoice + "** for you!"
        
client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
