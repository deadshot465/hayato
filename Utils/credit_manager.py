import asyncio
import discord
import json
import os
import random
import requests
from datetime import datetime
from discord.ext import commands
from distutils.util import strtobool
from marshmallow_dataclass import class_schema
from typing import List, Optional, Union
from Utils.authentication_manager import AuthenticationManager
from Utils.Structures.user_credit_item import UserCreditItem

HAYATO_PLUS_RESPONSES = [
    "Alright, <@{userId}>! You've successfully got {credits} credits!",
    "Way to go, <@{userId}>! You've got {credits} credits!",
    "<@{userId}>, you've got {credits} credits. Wow! That's amazing!",
    "<@{userId}>, you've got {credits} credits. Won't be long until you can buy a ticket to Osaka!",
    "Earing credits faster than Shinkansen E5, I see, <@{userId}>! You've got {credits} credits!"
]

HAYATO_MINUS_RESPONSES = [
    "Oh, snap, <@{userId}>! You've lost {credits} credits!",
    "How unfortunate, <@{userId}>... You've lost {credits} credits...",
    "Uhh...you've lost {credits} credits, <@{userId}>!",
    "Oh, no! You've lost {credits} credits, <@{userId}>!",
    "You've lost {credits} credits, <@{userId}>. That's worth a one-way ticket to Tokyo..."
]


class CreditManager:
    initialized = False
    fetch_from_server = False
    credits_path = 'Storage/credits.json'
    user_credits: List[UserCreditItem] = list()
    user_credit_item_schema = class_schema(UserCreditItem)
    last_fetch_time: datetime = datetime.now()

    @classmethod
    async def initialize(cls):
        cls.fetch_from_server = bool(strtobool(os.getenv('FETCH_FROM_SERVER'))) or False
        await cls.fetch(True)
        cls.initialized = True

    @classmethod
    async def get_user_credits(cls, ctx: commands.Context, user_id: int) -> int:
        if not cls.initialized:
            raise RuntimeError('The credit manager is not yet initialized.')
        await cls.fetch()
        items = list(filter(lambda x: x.UserId == str(user_id), cls.user_credits))
        if len(items) != 0:
            return items[0].Credits
        else:
            item = await cls.add_user(user_id, 100, ctx)
            return item.Credits

    @classmethod
    async def add_credits(cls, user_id: int, amount: int, *, channel_id: int = 0, insert: bool = False,
                          ctx: Optional[commands.Context] = None, channel: Optional[Union[discord.abc.Messageable]] = None) -> UserCreditItem:
        if not cls.initialized:
            raise RuntimeError('The credit manager is not yet initialized.')
        await cls.fetch(True)
        users = list(filter(lambda x: x.UserId == str(user_id), cls.user_credits))
        if not insert:
            if len(users) == 0:
                user = await cls.add_user(user_id, 100, ctx)
            else:
                user = users[0]
        else:
            if len(users) != 0:
                user = users[0]
            else:
                user = await cls.add_user(user_id, 100, ctx)
        user.Credits += amount
        await cls.update_user(user_id, amount, 'plus', channel_id=channel_id, ctx=ctx, channel=channel)
        return user

    @classmethod
    async def remove_credits(cls, user_id: int, amount: int, *, channel_id: int = 0,
                             ctx: Optional[commands.Context] = None, channel: Optional[Union[discord.abc.Messageable]] = None) -> UserCreditItem:
        if not cls.initialized:
            raise RuntimeError('The credit manager is not yet initialized.')
        await cls.fetch(True)
        users = list(filter(lambda x: x.UserId == str(user_id), cls.user_credits))
        if len(users) == 0:
            user = await cls.add_user(user_id, 100, ctx)
        else:
            user = users[0]
        user.Credits -= amount
        await cls.update_user(user_id, amount, 'minus', channel_id=channel_id, ctx=ctx, channel=channel)
        return user

    @classmethod
    async def fetch(cls, force: bool = False):
        if ((datetime.now() - cls.last_fetch_time).total_seconds() < 3600) and not force:
            return
        if cls.fetch_from_server:
            response = requests.get('https://tetsukizone.com/api/credit/')
            raw_json = response.text
            cls.user_credits = cls.user_credit_item_schema().loads(json_data=raw_json, many=True)
        else:
            with open(cls.credits_path) as file:
                cls.user_credits = cls.user_credit_item_schema().loads(json_data=file.read(), many=True)
                if cls.user_credits is None:
                    raise IOError("Failed to read from local file.")
        cls.last_fetch_time = datetime.now()

    @classmethod
    async def add_user(cls, user_id: int, amount: int, ctx: commands.Context) -> UserCreditItem:
        author: Union[discord.User, discord.Member] = ctx.author
        id = cls.user_credits[len(cls.user_credits) - 1].Id + 1
        user = UserCreditItem(id, str(author.name), str(user_id), amount)
        cls.user_credits.append(user)
        AuthenticationManager.login()
        if cls.fetch_from_server:
            data = {
                'Username': str(author.name),
                'UserId': str(user_id),
                'Credits': amount
            }
            raw_json = json.dumps(data)
            headers = {
                'Authorization': 'Bearer {}'.format(AuthenticationManager.token)
            }
            try:
                response = requests.post('https://tetsukizone.com/api/credit/', json=raw_json, headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                print('An error occurred when posting to the database: {}'.format(ex.response))
        else:
            with open(cls.credits_path, 'w') as file:
                serialized = cls.user_credit_item_schema().dumps(cls.user_credits)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
        return user

    @classmethod
    async def update_user(cls, user_id: int, amount: int, action: str, *, channel_id: int = 0,
                          ctx: Optional[commands.Context] = None, channel: Optional[Union[discord.abc.Messageable]] = None):
        AuthenticationManager.login()
        if cls.fetch_from_server:
            data = {
                'Credit': amount,
                'ChannelId': str(channel_id)
            }
            headers = {
                'Authorization': 'Bearer {}'.format(AuthenticationManager.token)
            }
            try:
                response = requests.patch('https://tetsukizone.com/api/credit/{}/{}'.format(user_id, action), json=json.dumps(data), headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                print('An error occurred when patching to the database: {}'.format(ex.response))
        else:
            with open(cls.credits_path, 'w') as file:
                serialized = cls.user_credit_item_schema().dumps(cls.user_credits, many=True)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
            if channel_id != 0:
                if ctx is not None:
                    if action == 'plus':
                        await ctx.send(
                            random.choice(HAYATO_PLUS_RESPONSES).replace('{userId}', str(user_id)).replace('{credits}',
                                                                                                           str(amount)))
                    elif action == 'minus':
                        await ctx.send(
                            random.choice(HAYATO_MINUS_RESPONSES).replace('{userId}', str(user_id)).replace('{credits}',
                                                                                                            str(
                                                                                                                amount)))
                elif channel is not None:
                    if action == 'plus':
                        await channel.send(
                            random.choice(HAYATO_PLUS_RESPONSES).replace('{userId}', str(user_id)).replace('{credits}',
                                                                                                           str(amount)))
                    elif action == 'minus':
                        await channel.send(
                            random.choice(HAYATO_MINUS_RESPONSES).replace('{userId}', str(user_id)).replace('{credits}',
                                                                                                            str(
                                                                                                                amount)))
        await cls.fetch(True)
