import json
import logging
import os
import random
import typing
from datetime import datetime

import requests
from marshmallow_dataclass import class_schema
from services.authentication_service import AuthenticationService
from services.configuration_service import configuration_service
from structures.lottery.user_credit_item import UserCreditItem

HAYATO_PLUS_RESPONSES: typing.Final[list[str]] = [
    "Alright, <@{userId}>! You've successfully got {credits} credits!",
    "Way to go, <@{userId}>! You've got {credits} credits!",
    "<@{userId}>, you've got {credits} credits. Wow! That's amazing!",
    "<@{userId}>, you've got {credits} credits. Won't be long until you can buy a ticket to Osaka!",
    "Earning credits faster than Shinkansen E5, I see, <@{userId}>! You've got {credits} credits!"
]

HAYATO_MINUS_RESPONSES: typing.Final[list[str]] = [
    "Oh, snap, <@{userId}>! You've lost {credits} credits!",
    "How unfortunate, <@{userId}>... You've lost {credits} credits...",
    "Uhh...you've lost {credits} credits, <@{userId}>!",
    "Oh, no! You've lost {credits} credits, <@{userId}>!",
    "You've lost {credits} credits, <@{userId}>. That's worth a one-way ticket to Tokyo..."
]


class CreditService:
    _credits_path = 'lottery/credits.json'
    _user_credits: list[UserCreditItem] = list()
    _user_credit_item_schema = class_schema(UserCreditItem)
    _last_fetch_time: datetime = datetime.now()

    def __init__(self):
        self._fetch_from_server = configuration_service.fetch_from_server
        self._initialized = False

    async def add_credits(self, *, user_id: int, user_name: str, amount: int) -> UserCreditItem:
        await self.__fetch(True)
        users = list(filter(lambda x: x.UserId == str(user_id), self._user_credits))
        if len(users) == 0:
            user = await self.__add_user(user_id, user_name, 100)
        else:
            user = users.pop(0)
        user.Credits += amount
        await self.__update_user(user_id=user_id, amount=amount, action='plus')
        return user

    async def get_user_credits(self, user_id: int, user_name: str) -> int:
        await self.__fetch(not self._initialized)
        items = list(filter(lambda x: x.UserId == str(user_id), self._user_credits))
        if len(items) != 0:
            return items.pop(0).Credits
        else:
            item = await self.__add_user(user_id, user_name, 100)
            return item.Credits

    async def remove_credits(self, *, user_id: int, user_name: str, amount: int) -> UserCreditItem:
        await self.__fetch(True)
        users = list(filter(lambda x: x.UserId == str(user_id), self._user_credits))
        if len(users) == 0:
            user = await self.__add_user(user_id, user_name, 100)
        else:
            user = users.pop(0)
        user.Credits -= amount
        await self.__update_user(user_id=user_id, amount=amount, action='minus')
        return user

    async def replenish(self):
        users_to_replenish = list(filter(lambda x: x.Credits <= 200, self._user_credits))
        for user in users_to_replenish:
            user.Credits += 200
            await self.__update_user(user_id=int(user.UserId), amount=200, action='plus')

    async def __add_user(self, user_id: int, user_name: str, amount: int) -> UserCreditItem:
        if len(self._user_credits) == 0:
            new_user_id = 0
        else:
            new_user_id = self._user_credits[len(self._user_credits) - 1].Id + 1
        new_user = UserCreditItem(new_user_id, user_name, str(user_id), amount)
        self._user_credits.append(new_user)
        AuthenticationService.login()
        if self._fetch_from_server:
            data = {
                'Username': user_name,
                'UserId': user_id,
                'Credits': amount
            }
            raw_json = json.dumps(data)
            headers = {
                'Authorization': 'Bearer {}'.format(AuthenticationService.token)
            }
            try:
                response = requests.post('https://tetsukizone.com/api/credit/', json=raw_json, headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                logging.error('An error occurred when posting to the database: %s' % ex.response)
        else:
            with open(self._credits_path, 'w') as file:
                serialized = self._user_credit_item_schema().dumps(self._user_credits, many=True)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
        return new_user

    async def __fetch(self, force: bool = False):
        if ((datetime.now() - self._last_fetch_time).total_seconds() < 3600) and not force:
            return
        if self._fetch_from_server:
            response = requests.get('https://tetsukizone.com/api/credit/')
            raw_json = response.text
            self._user_credits = self._user_credit_item_schema().loads(json_data=raw_json, many=True)
        else:
            with open(self._credits_path) as file:
                self._user_credits = self._user_credit_item_schema().loads(json_data=file.read(), many=True)
                if self._user_credits is None:
                    logging.error("Failed to read from local file.")
        self._last_fetch_time = datetime.now()
        if not self._initialized:
            self._initialized = True

    async def __update_user(self, *, user_id: int, amount: int, action: str, channel_id: int = 0):
        AuthenticationService.login()
        if self._fetch_from_server:
            data = {
                'Credit': amount,
                'ChannelId': str(channel_id)
            }
            headers = {
                'Authorization': 'Bearer {}'.format(AuthenticationService.token)
            }
            try:
                response = requests.patch('https://tetsukizone.com/api/credit/{}/{}'.format(user_id, action),
                                          json=json.dumps(data), headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                logging.error('An error occurred when patching to the database: %s' % ex.response)
        else:
            with open(self._credits_path, 'w') as file:
                serialized = self._user_credit_item_schema().dumps(self._user_credits, many=True)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
        await self.__fetch(True)


credit_service = CreditService()
