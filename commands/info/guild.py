import hikari
from lightbulb import slash_commands
from services.configuration_service import configuration_service
from utils.constants import HAYATO_COLOR
from utils.utils import get_author_name


class Guild(slash_commands.SlashCommand):
    description: str = 'Get the information about this server.'
    enabled_guilds: list[int] = [705036924330704968]

    async def callback(self, context) -> None:
        author = context.author
        member = context.member
        guild = context.guild
        bot_user = configuration_service.bot.get_me()
        avatar_url = author.avatar_url or author.default_avatar_url
        embed = hikari.Embed(color=HAYATO_COLOR,
                             title='Server Information',
                             description=f'Here is the detailed information of {guild.name}.')
        embed.set_author(name=get_author_name(author, member), icon=avatar_url)
        embed.set_thumbnail(guild.icon_url)

        if guild.banner_url is not None:
            embed.add_field(name='Banner URL', value=str(guild.banner_url), inline=False)

        embed.add_field(name='Creation Date', value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)

        if guild.description is not None:
            embed.add_field(name='Description', value=guild.description, inline=False)

        feature_count = len(guild.features)
        if feature_count > 0:
            embed.add_field(name='Features', value=', '.join(guild.features), inline=False)

        embed.add_field(name='Guild ID', value=str(guild.id), inline=False)

        owner = await guild.fetch_owner()
        embed.add_field(name='Owner',
                        value='{}#{} [{}]'.format(owner.display_name, owner.discriminator, owner.id),
                        inline=False)

        if guild.splash_url is not None:
            embed.add_field(name='Splash URL', value=str(guild.splash_url), inline=False)

        embed.add_field(name='Members', value=str(guild.member_count), inline=True)
        embed.add_field(name='Preferred Locale', value=guild.preferred_locale, inline=True)
        await context.respond(embed)
