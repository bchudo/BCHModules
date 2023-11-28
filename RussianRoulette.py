# meta developer: @bchmodules
# meta pic: https://0x0.st/HwtW.jpg
# meta banner: https://0x0.st/HwFg.jpg

from .. import loader, utils
from telethon.tl.types import Message
import asyncio
import logging
from telethon.tl.functions.channels import JoinChannelRequest
import random
import time
import subprocess
from ..inline.types import InlineCall
import sys


@loader.tds
class RussianRouletteMod(loader.Module):
    """Русская рулетка"""

    strings_ru = {
        "name": "RussianRoulette",
        "win": "🥳 <b>Вы победили!</b>",
        "lose": "😓 <b>Вы проиграли!</b>",
        "userbot_working": "✔️ <b>Юзербот снова работает.</b>",
        "go_play": "<b>Поиграем</b> 😏",
    }
    strings = {
        "name": "RussianRoulette",
        "win": "🥳 <b>You win!</b>",
        "lose": "😓 <b>You lose!</b>",
        "userbot_working": "✔️ <b>Userbot is working again.</b>",
        "go_play": "<b>Go play</b> 😏",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "suspend_time",
                300,
                "Suspend time in seconds",
                loader.validators.Integer(minimum=30),
            ),
            loader.ConfigValue(
                "stop_userbot",
                True,
                "Stop userbot if you lose",
                loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "rows", 
                8, 
                "Rows", 
                loader.validators.Integer(minimum=2, maximum=50)
            ),
            loader.ConfigValue(
                "columns",
                8,
                "Columns",
                loader.validators.Integer(minimum=2, maximum=50),
            ),
            loader.ConfigValue(
                "disable_security",
                False,
                "Will outsiders be able to press buttons?",
                loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        try:
            channels = [await self.client.get_entity("t.me/bchmodules")]
            await client(JoinChannelRequest(channels[0]))
        except Exception as e:
            logger.error(f"Can't join channels\n{e}")

    async def return_buttons(self):
        rows, columns = self.config["rows"], self.config["columns"]
        pam = [True, False]
        buttons = [
            [
                {"text": " ", "callback": self.lose}
                if random.choice(pam)
                else {"text": " ", "callback": self.win}
                for i in range(rows)
            ]
            for j in range(columns)
        ]
        return buttons

    async def lose(self, call: InlineCall):
        await call.edit(self.strings("lose"))
        if self.config["stop_userbot"]:
            sys.exit(0)
        else:
            time.sleep(self.config["suspend_time"])
            await call.edit(self.strings("userbot_working"))

    async def win(self, call: InlineCall):
        await call.edit(self.strings("win"))

    @loader.command(ru_doc="играть в русскую рулетку", alias="rr")
    async def rrplaycmd(self, message):
        """play to russian roulette"""
        await self.inline.form(
            text=self.strings("go_play"),
            reply_markup=(await self.return_buttons()),
            message=message,
            disable_security=True if self.config["disable_security"] else False,
        )
