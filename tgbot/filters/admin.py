from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config


class AdminGroupFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        return (str(obj.chat.id) == config.misc.admin_group) == self.is_admin


class AdminIdFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        return (obj.from_user.id in config.tg_bot.admin_ids) == self.is_admin
