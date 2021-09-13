import hikari
from lightbulb import slash_commands
from services.configuration_service import configuration_service
from utils.constants import HAYATO_COLOR, LAST_UPDATE_DATE, PYTHON_LOGO, VERSION


class About(slash_commands.SlashCommand):
    description: str = 'See the information about Hayato.'

    async def callback(self, context) -> None:
        bot_user = configuration_service.bot.get_me()
        avatar_url = bot_user.avatar_url or bot_user.default_avatar_url
        embed = hikari.Embed(color=HAYATO_COLOR,
                             description='Hayato the best boi is inspired by the anime Shinkalion. It is written with '
                                         'the awesome [Hikari](https://github.com/davfsa/hikari) library and '
                                         '[Lightbulb](https://github.com/tandemdude/hikari-lightbulb) library for '
                                         'command handlers, but new features will be added from time to time.\n\n'
                                         f'Hayato version {VERSION} was made and developed by:\n'
                                         '**Kirito#9286** and **Tetsuki Syu#1250**\nHayato Bot is licensed '
                                         'under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html')
        embed.set_footer(text=f'Hayato Bot: Release {VERSION} | {LAST_UPDATE_DATE}')
        embed.set_author(name='Hayasugi Hayato from Shinkalion', icon=avatar_url)
        embed.set_thumbnail(PYTHON_LOGO)
        await context.respond(embed)
