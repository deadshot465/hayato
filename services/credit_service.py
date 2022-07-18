import json
import logging
import random
import typing
from datetime import datetime

import requests
from marshmallow_dataclass import class_schema

from services.authentication_service import AuthenticationService
from services.configuration_service import configuration_service
from structures.lottery.user_credit import UserCredit

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
    _user_credits: list[UserCredit] = list()
    _user_credit_schema = class_schema(UserCredit)
    _last_fetch_time: datetime = datetime.now()

    def __init__(self):
        self._fetch_from_server = configuration_service.fetch_from_server
        self._initialized = False

    async def add_credits(self, *, user_id: int, user_name: str, amount: int) -> UserCredit:
        await self.fetch(True)
        users = (item for item in self._user_credits if item.user_id == str(user_id))
        found_user = next(users, -1)
        if found_user == -1:
            user = await self.__add_user(user_id, user_name, 100)
        else:
            user = found_user
        user.credits += amount
        await self.__update_user(user_id=str(user_id), amount=amount, action='plus')
        return user

    async def get_user_credits(self, user_id: int, user_name: str, force: bool = False) -> int:
        await self.fetch(not self._initialized or force)
        items = (item for item in self._user_credits if item.user_id == str(user_id))
        found_item = next(items, -1)
        if found_item != -1:
            return found_item.credits
        else:
            item = await self.__add_user(user_id, user_name, 100)
            return item.credits

    async def remove_credits(self, *, user_id: int, user_name: str, amount: int) -> UserCredit:
        await self.fetch(True)
        users = (item for item in self._user_credits if item.user_id == str(user_id))
        found_user = next(users, -1)
        if found_user == -1:
            user = await self.__add_user(user_id, user_name, 100)
        else:
            user = found_user
        user.credits -= amount
        await self.__update_user(user_id=str(user_id), amount=amount, action='minus')
        return user

    async def replenish(self):
        users_to_replenish = [x for x in self._user_credits if x.credits <= 200]
        for user in users_to_replenish:
            user.credits += 200
            await self.__update_user(user_id=user.user_id, amount=200,
                                     action='plus')
            yield random.choice(HAYATO_PLUS_RESPONSES) \
                .replace('{userId}', user.user_id) \
                .replace('{credits}', str(200))

    async def __add_user(self, user_id: int, user_name: str, amount: int) -> UserCredit:
        if len(self._user_credits) == 0:
            new_user_id = 0
        else:
            sorted_ids = [int(x.id) for x in sorted(self._user_credits, key=lambda y: int(y.id), reverse=True)]
            new_user_id = sorted_ids[0] + 1
        new_user = UserCredit(str(new_user_id), user_name, str(user_id), amount)
        self._user_credits.append(new_user)
        AuthenticationService.login()
        if self._fetch_from_server:
            headers = {
                'Authorization': f'Bearer {AuthenticationService.token}'
            }
            try:
                response = requests.post(configuration_service.api_endpoint + '/credit/',
                                         json=self._user_credit_schema().dumps(new_user), headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                logging.error('An error occurred when posting to the database: %s' % ex.response)
        else:
            with open(self._credits_path, 'w') as file:
                serialized = self._user_credit_schema().dumps(self._user_credits, many=True)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
        return new_user

    async def fetch(self, force: bool = False):
        if ((datetime.now() - self._last_fetch_time).total_seconds() < 3600) and not force:
            return

        if self._fetch_from_server:
            AuthenticationService.login()
            headers = {
                'Authorization': f'Bearer {AuthenticationService.token}'
            }
            try:
                response = requests.get(configuration_service.api_endpoint + '/credit', headers=headers)
                response.raise_for_status()
                raw_json = response.text
                self._user_credits = self._user_credit_schema().loads(json_data=raw_json, many=True)
            except requests.exceptions.HTTPError as ex:
                error_message = f'Failed to fetch user credits from server: {ex.response}'
                logging.error(error_message)
        else:
            with open(self._credits_path) as file:
                self._user_credits = self._user_credit_schema().loads(json_data=file.read(), many=True)
                if self._user_credits is None:
                    logging.error("Failed to read from local file.")
        self._last_fetch_time = datetime.now()
        if not self._initialized:
            self._initialized = True

    async def __update_user(self, *, user_id: str, amount: int, action: str):
        AuthenticationService.login()
        if self._fetch_from_server:
            data = {
                'credit': amount
            }
            headers = {
                'Authorization': f'Bearer {AuthenticationService.token}'
            }
            try:
                response = requests.patch(configuration_service.api_endpoint + f'/credit/{user_id}/{action}',
                                          json=json.dumps(data), headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                logging.error('An error occurred when patching to the database: %s' % ex.response)
        else:
            with open(self._credits_path, 'w') as file:
                serialized = self._user_credit_schema().dumps(self._user_credits, many=True)
                obj = json.loads(serialized)
                file.write(json.dumps(obj, indent=2))
        await self.fetch(True)

    @property
    def user_credits(self) -> typing.Dict[str, UserCredit]:
        result = dict()
        for user_credit in self._user_credits:
            result[user_credit.user_id] = user_credit
        return result


credit_service = CreditService()
