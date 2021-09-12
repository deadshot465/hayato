import datetime
import logging
import os.path
import typing

import lightbulb
import yaml

from services.credit_service import credit_service
from structures.lottery.lottery import Lottery
from structures.lottery.lottery_participant import LotteryParticipant


class LotteryService:
    _directory_name = 'lottery'
    _file_name = 'lottery.yaml'
    _file_path = os.path.join(os.getcwd(), _directory_name, _file_name)

    def __init__(self):
        self._bot: typing.Optional[lightbulb.Bot] = None
        self._lottery_running = False
        if not os.path.isdir(self._directory_name):
            os.mkdir(self._directory_name)
        if os.path.exists(self._file_path):
            with open(self._file_path) as file:
                s = file.read()
                self._lottery: Lottery = yaml.load(s, Loader=yaml.SafeLoader)
        else:
            self._lottery = Lottery()
            self.write_lottery()

    @property
    def lottery_channel_id(self) -> int:
        return self._lottery.lottery_info.channel_id

    @property
    def lottery_scheduled(self) -> datetime.datetime:
        return self._lottery.lottery_info.lottery_scheduled

    @lottery_scheduled.setter
    def lottery_scheduled(self, value: datetime.datetime):
        self._lottery.lottery_info.lottery_scheduled = value

    @property
    def bot(self) -> typing.Optional[lightbulb.Bot]:
        return self._bot

    @bot.setter
    def bot(self, value: lightbulb.Bot) -> None:
        self._bot = value

    @property
    def lottery_running(self) -> bool:
        return self._lottery_running

    async def buy_lottery(self, user_id: int, user_name: str, numbers: set[int]):
        if self._lottery_running:
            return 'There is a lottery running now! Please try again after the lottery is over!'
        user_credits = await credit_service.get_user_credits(user_id, user_name)
        if user_credits - 10 < 0:
            return 'You don\'t have enough credits to buy the lottery!'

        await credit_service.remove_credits(user_id=user_id, user_name=user_name, amount=10)
        participant = self.get_participant(user_id)
        sorted_numbers = sorted(numbers)
        if participant is None:
            participant = LotteryParticipant(user_id=user_id, user_name=user_name)
            participant.lotteries.append(sorted_numbers)
            self._lottery.lottery_participants.append(participant)
            response = '%s, you have got your 100 starting credits! You have successfully bought a lottery of `%s`!'\
                       % (user_name, str(sorted_numbers))
        else:
            participant.lotteries.append(sorted_numbers)
            if participant.user_name != user_name:
                participant.user_name = user_name
            response = '%s, you have successfully bought a lottery of `%s`! Deducted 10 credits from your account.'\
                       % (user_name, str(sorted_numbers))
        self.write_lottery()
        return response

    def get_participant(self, user_id: int) -> typing.Optional[LotteryParticipant]:
        participant = list(filter(lambda p: p.user_id == user_id, self._lottery.lottery_participants))
        if len(participant) == 0:
            return None
        else:
            return participant.pop(0)

    def set_next_lottery_time(self):
        if datetime.datetime.today().weekday() == 3:
            self.lottery_scheduled += datetime.timedelta(days=3)
        elif datetime.datetime.today().weekday() == 6:
            self.lottery_scheduled += datetime.timedelta(days=4)
        logging.info('Next lottery date: ' + str(self.lottery_scheduled))
        self.write_lottery()

    def write_lottery(self):
        with open(self._file_path, 'w') as file:
            s = yaml.dump(self._lottery, Dumper=yaml.SafeDumper)
            file.write(s)


lottery_service = LotteryService()
