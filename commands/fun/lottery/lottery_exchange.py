import json
import logging

import hikari
import lightbulb
import requests

from commands.fun.lottery.lottery import lottery
from services.configuration_service import configuration_service
from services.credit_service import credit_service
from utils.constants import LOTTERY_ICON, HAYATO_COLOR
from utils.utils import get_author_name


@lottery.child
@lightbulb.option('amount',
                  'The amount of credits you want to change to Jack of All Trades\' tips. 1 credit = 10 tips.',
                  required=True, min_value=0, type=int)
@lightbulb.command('exchange', 'Exchange for Jack of All Trades\' tips with your credits. 1 credit = 10 tips.',
                   auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def exchange(ctx: lightbulb.Context) -> None:
    amount: int = ctx.options.amount
    author_name = get_author_name(ctx.author, ctx.member)
    user_credit = await credit_service.get_user_credits(int(ctx.author.id), author_name, True)
    if user_credit - amount < 0:
        await ctx.respond(content='You cannot exchange with an amount more than what you currently have!')
        return

    try:
        payload = {
            'adjustment': 'Plus',
            'new_amount': amount * 10
        }
        headers = {
            'Content-Type': 'application/json'
        }
        logging.info(json.dumps(payload))
        endpoint = f'{configuration_service.joat_endpoint}/tip/{int(ctx.author.id)}'
        response = requests.patch(endpoint, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        author_credit_item = await credit_service.remove_credits(user_id=int(ctx.author.id),
                                                                 user_name=author_name, amount=amount)
        response = requests.get(endpoint)
        response.raise_for_status()
        new_joat_tips: int = response.json()['amount']
        embed = hikari.Embed(title='Exchange Credits',
                             description=f'You have successfully exchanged {amount * 10} Jack of All Trades tips with'
                                         f' {amount} credits!\'', colour=HAYATO_COLOR)\
            .set_author(name=author_name, icon=ctx.author.avatar_url or ctx.author.default_avatar_url)\
            .add_field('Lottery Balance', str(author_credit_item.credits), inline=True)\
            .add_field('Jack of All Trades Balance', str(new_joat_tips), inline=True)\
            .set_thumbnail(LOTTERY_ICON)
        await ctx.respond(embed=embed)
    except requests.exceptions.HTTPError as ex:
        logging.error('An error occurred when patching to the database: %s' % ex.response)
        await ctx.respond(f'Sorry, but I can\'t seem to exchange tips for you! '
                          f'Have you joined Jack of All Trades already?')
