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

        if message.content == 'h!about':
            avatar_url = str(self.user.avatar_url)
            embed = discord.Embed(color=discord.Color.from_rgb(30, 99, 175),
                                  description='Hayato the best boi is inspired by the anime Shinkalion. It is meant for practising making a Discord bot in Discord.py, but new features will be added from time to time.\n\nHayato version 1.0 was made and developed by:\n**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html').set_footer(
                text='Hayato Bot: Release 1.0 | 2020-07-28').set_author(name='Hayasugi Hayato from Shinkalion',
                                                                        icon_url=avatar_url).set_thumbnail(
                url='https://pbs.twimg.com/profile_images/1245939758695510016/UOG9MGdU_400x400.png')
            await message.channel.send(embed=embed)
        
        if message.content == 'h!help':
            await message.channel.send('Here is a list of commands for Hayato:\n`cvt` Convert units. Celsius/Fahrenheit and kg/lbs converter is available.\n`dashsep` Separate every letter of your input with a dash.\n`fascinated` Sends a certain number KouFascinated emote.\n`pick` Hayato will help you pick one choice randomly.\n`verifyemail` Check if the email is plausible.\n`vowels` Count the number of vowels in the input.')
            
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

        if message.content.startswith('h!cvt'):
            user_input = message.content[6:]
            answer = self.cvt(user_input)
            await message.channel.send(str(answer[0]) + answer[2] + ' is equal to ' + str(answer[1]) + answer[3] + '!')

        if message.content.startswith('h!pick'):
            user_input = message.content[7:]
            answer = self.pick(user_input)
            await message.channel.send(answer) 
            
        if message.content.startswith('h!fascinated'):
            user_input = message.content[13:]
            answer = self.fascinated(user_input)
            await message.channel.send(answer) 
            
        if message.content.startswith('h!verifyemail'):
            user_input = message.content[14:]
            answer = self.verify_email(user_input)
            await message.channel.send(answer)  
            
        # Switch presence every hour
        if (datetime.now() - self.last_updated).seconds > 3600:
            await self.switch_presence()
            self.last_updated = datetime.now()

    # Count vowels
    def count_vowels(self, string: str) -> int:
        count = 0
        for letter in string:
            if letter in 'AEIOUaeiou':
                count += 1
        return count
    
    # Dash separator
    def dash_separator(self, string: str) -> str:
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
    
    # Converter
    def cvt(self, user_input):
        source = ''
        target = ''
        unit_source = ''
        unit_target = ''
        if 'f c' in user_input:
            source = float(user_input[4:])
            target = round((source - 32) * 5 / 9, 2)
            unit_source = '\u2109'
            unit_target = '\u2103'
        if 'c f' in user_input:
            source = float(user_input[4:])
            target = round(source * 9 / 5 + 32, 2)
            unit_source = '\u2103'
            unit_target = '\u2109'
        if 'lbs kg' in user_input:
            source = float(user_input[7:])
            target = source / 2.2
            unit_source = 'lbs'
            unit_target = 'kg'
        if 'kg lbs' in user_input:
            source = float(user_input[7:])
            target = source * 2.2
            unit_source = 'kg'
            unit_target = 'lbs'
        if 'inch cm' in user_input:
            source = float(user_input[8:])
            target = source * 2.54
            unit_source = 'inch'
            unit_target = 'cm'
        if 'cm inch' in user_input:
            source = float(user_input[8:])
            target = source / 2.54
            unit_source = 'cm'
            unit_target = 'inch'
        return source, target, unit_source, unit_target


    # Random pick
    def pick(self, all_choices: str) -> str:
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
    
    # KouFascinated    
    def fascinated(self, count):
        result = ''
        if count == '':
            result = 'https://cdn.discordapp.com/emojis/705279783340212265.gif'
        else:
            for i in range(0, int(count)):
                result += '<a:KouFascinated:705279783340212265> '
        return result

    DOMAINS = {'com', 'net', 'hk', 'org', 'ca', 'info'}
    
    def check_name_or_host(self, input_string):
        '''
        (str) -> bool
        
        Return True if the name or host obeys the following rules:
        - NAME, HOST cannot contain any of {(, ), @, space}
        - NAME, HOST must be in between 1 and 100 characters
        >>> utoronto
        True
        >>> marco.miu
        True
        >>> de@gh(fe)
        False
        '''
        # Check if the name of host contains '(' or ')' or '@' or ' '
        # If there is, we have found an error   
        error = False
        if '(' in input_string or ')' in input_string or '@' in input_string or ' ' in input_string:
            error = True
        else:
        # Else, check the length of the name and host
        # If the length is out the allowed range, we have found an error
            if len(input_string) < 1 or len(input_string) > 100:
                error = True
                
        return not error
        
    def verify_email(self, email: str) -> str:
        '''
        Return True if and only if the email is valid according to the following rules:
        - Must be formatted as NAME@HOST.DOMAIN
        - NAME, HOST cannot contain any of {(, ), @, space}
        - NAME, HOST must be in between 1 and 100 characters
        - DOMAIN must be in the set listed
        >>> verify_email('abc@def.com')
        True
        >>> verify_email('ab@c@de.f@.gh')
        False
        '''
        # Start of assuming no errors
        found_error = False
        # First check whether we can split the name, host and domain
        # If we cannot find @ and dot, there is an error
        if not '@' in email or not '.' in email:
            found_error = True
        # else find the index of @ and .
        else:
            at_index = email.index('@')
            dot_index = email.rindex('.')
        # if index of @ > index of ., there is an error
            if at_index > dot_index:
                found_error = True
        # else we can split
            else:
                name = email[0:at_index]
                host = email[at_index + 1:dot_index]
                domain = email[dot_index + 1:]
       
        # Check name and host
        valid_name = self.check_name_or_host(name)
        valid_host = self.check_name_or_host(host)
        if valid_name == False or valid_host == False:
            found_error = True
        # Check domain
        if not domain in self.DOMAINS:
            found_error = True
        
        if found_error == True:
            return "This email is not plausible!"
        else:
            return "This email is plausible!"
    
client = MyClient()
client.run('NzM3MDE3MjMxNTIyOTIyNTU2.Xx3OyQ.YondP6gak5j5G4jzTJx88IKzPRM')
