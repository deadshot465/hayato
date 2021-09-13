import asyncio
import datetime
import logging
import os.path
import random
import typing

import hikari
import lightbulb
import yaml
from services.credit_service import credit_service
from structures.lottery.lottery import Lottery
from structures.lottery.lottery_participant import LotteryParticipant
from utils.constants import HAYATO_COLOR, LOTTERY_ICON


class LotteryService:
    _directory_name = 'lottery'
    _file_name = 'lottery.yaml'
    _file_path = os.path.join(os.getcwd(), _directory_name, _file_name)
    _word_list: typing.Final[str] = ['first', 'second', 'third', 'fourth', 'fifth', 'last']
    _rewards: typing.Final[dict[int, int]] = {
        0: 0,
        1: 0,
        2: 20,
        3: 100,
        4: 1000,
        5: 2000,
        6: 6000
    }

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

    async def auto_lottery(self, bot: lightbulb.Bot, channel: hikari.TextableGuildChannel):
        running_message = ''
        drawn_numbers: list[int] = []
        msg_generator = self.start_lottery()
        initial_message = await channel.send('The lottery will start in 10 seconds!')

        try:
            while True:
                s, i = await msg_generator.__anext__()
                running_message += s + '\n'
                drawn_numbers.append(i)
                await initial_message.edit(running_message)
                await asyncio.sleep(3.0)
        except StopAsyncIteration:
            pass

        running_message += 'The drawn numbers are: ' + ''.join(str(drawn_numbers))
        await initial_message.edit(running_message)

        result_generator = self.build_lottery_result(drawn_numbers)
        try:
            while True:
                res = await result_generator.__anext__()
                if isinstance(res, hikari.Embed):
                    await channel.send(embed=res)
                else:
                    await channel.send(res)
                await asyncio.sleep(1.0)
        except StopAsyncIteration:
            return

    async def build_lottery_result(self, drawn_numbers: list[int]):
        embed = hikari.Embed(title='Lottery Result', color=HAYATO_COLOR)\
            .set_thumbnail(LOTTERY_ICON)
        result_text = ''

        for participant in self._lottery.lottery_participants:
            participant_lotteries = participant.lotteries

            if len(participant_lotteries) == 0:
                continue

            total_credits = 0

            for i, lottery in enumerate(participant_lotteries):
                hit_numbers = [x for x in lottery if x in drawn_numbers]
                hit_count = len(hit_numbers)
                reward = self._rewards[hit_count]
                total_credits += reward
                result_text += f'{participant.user_name}\'s lottery #{i + 1} hits **{hit_count}** numbers!' \
                               f' You gained **{reward}** credits!\n'
                if len(result_text) >= 1900:
                    yield result_text
                    result_text = ''

            if total_credits != 0:
                await credit_service.add_credits(user_id=participant.user_id, user_name=participant.user_name,
                                                 amount=total_credits)
                embed.add_field(name=participant.user_name, value=str(total_credits), inline=True)

            participant_lotteries.clear()

        yield result_text
        yield embed
        msg_generator = credit_service.replenish(channel_id=self._lottery.lottery_info.channel_id)
        try:
            while True:
                s = await msg_generator.__anext__()
                yield s
        except StopAsyncIteration:
            pass
        self._lottery_running = False
        self.write_lottery()

    async def bulk_purchase(self, user_id: int, user_name: str, numbers: list[list[int]]) -> str:
        if self._lottery_running:
            return 'There is a lottery running now! Please try again after the lottery is over!'

        user_credits = await credit_service.get_user_credits(user_id, user_name)
        total_count = len(numbers)
        total_cost = 10 * total_count
        await credit_service.remove_credits(user_id=user_id, user_name=user_name, amount=total_cost)
        participant = self.get_participant(user_id)
        if participant is None:
            participant = LotteryParticipant(user_id=user_id, user_name=user_name)
            participant.lotteries = numbers
            self._lottery.lottery_participants.append(participant)
            response = '%s, you have got your 100 starting credits! You have successfully bulk purchased %d' \
                       ' lotteries! Deducted %d credits from your account.' % (user_name, total_count, total_cost)
        else:
            participant.lotteries.extend(numbers)
            if participant.user_name != user_name:
                participant.user_name = user_name
            response = '%s, you have successfully bulk purchased %d lotteries! Deducted %d credits from your' \
                       ' account.' % (user_name, total_count, total_cost)
        self.write_lottery()
        return response

    async def buy_lottery(self, user_id: int, user_name: str, numbers: set[int]) -> str:
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
        participants = (p for p in self._lottery.lottery_participants if p.user_id == user_id)
        participant = next(participants, -1)
        if participant == -1:
            return None
        else:
            return participant

    def set_next_lottery_time(self):
        if datetime.datetime.today().weekday() == 3:
            self.lottery_scheduled += datetime.timedelta(days=3)
        elif datetime.datetime.today().weekday() == 6:
            self.lottery_scheduled += datetime.timedelta(days=4)
        else:
            self.lottery_scheduled += datetime.timedelta(days=7)
        logging.info('Next lottery date: ' + str(self.lottery_scheduled))
        self.write_lottery()

    async def start_lottery(self):
        self._lottery_running = True
        await asyncio.sleep(10)
        drawn_numbers: set[int] = set()
        while len(drawn_numbers) != 6:
            drawn_numbers.add(random.randint(1, 49))
        order_and_num = zip(self._word_list, sorted(drawn_numbers))
        for w, i in order_and_num:
            yield 'The %s drawn number is **%d**!' % (w, i), i

    def write_lottery(self):
        with open(self._file_path, 'w') as file:
            s = yaml.dump(self._lottery, Dumper=yaml.SafeDumper)
            file.write(s)


lottery_service = LotteryService()
