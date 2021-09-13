import re
import typing

import hikari


USER_MENTION_REGEX = re.compile(r'<@!?(\d{17,20})>')
USER_TAG = re.compile(r'(\S.{0,30}\S)\s*#(\d{4})')
DISCORD_ID = re.compile(r'\d{17,20}')


def get_author_name(user: hikari.User, member: typing.Optional[hikari.Member]) -> str:
    if member is None:
        return user.username
    else:
        return member.display_name
