# meta developer: @bchmodules
# meta pic: https://0x0.st/HwtW.jpg
# meta banner: https://0x0.st/Hwtv.jpg

from .. import loader, utils

import random
from contextlib import suppress
from telethon.tl.types import Message
import requests
from bs4 import BeautifulSoup
import datetime

@loader.tds
class AbdullahMod(loader.Module):
    """Раб Аллаха."""
    strings = {
        "name": "Abdullah",
        "hadis_wrong": "❌ Error. Right use: <hadis number>. \nExample: .bukhari 1190",
        "ayat_wrong": "❌ Error. Right use: <surah:ayat>. \nExample: .ayat 2:255"
    }
    strings_ru = {
        "name": "Abdullah",
        "hadis_wrong": "❌ Ошибка. Правильное использование: <номер хадиса>. Пример: .bukhari 1190",
        "ayat_wrong": "❌ Ошибка. Правильное использование: <сура:аят>. Пример: .ayat 2:255"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "only_me",
                True,
                "Для кого будет доступен модуль? Если True - только клиенту, False - всем, кто пишет команды .ayat <сура:аят>",
                validator = loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "hadis_lang",
                "English",
                "Язык, на котором будут хадисы. РУССКИЙ МОЖЕТ ПЕРЕВОДИТЬСЯ НЕПРАВИЛЬНО",
                validator = loader.validators.Choice(["English", "Arabic", "Russian"])
            )
        )
    
    def day_to_ramadan():
        target_date = datetime.date(2024, 3, 11)
        today = datetime.date.today()
        remaining_time = target_date - today
        return remaining_time.days
    
    @loader.command(
        ru_doc="Сколько дней до Рамадана 2024?",
        en_doc="How many days are left before the Ramadan?"
    )
    async def ramadancmd(self, message: Message):
        await utils.answer(message=message, response=f"🎉 До Священного месяца Рамадан осталось: {day_to_ramadan()} дней!")
    
    @loader.command(
        ru_doc="<номер хадиса Сахих Муслим>",
        en_doc="<hadis number sahih Muslim>"
    )
    async def muslimcmd(self, message: Message):
        """<hadis number sahih Muslim>"""
        args = utils.get_args_raw(message)
        if args and args is not None:
            try:
                args = int(args)
                url = f"https://sunnah.com/muslim:{args}"
                html = (requests.get(url)).text
                soup = BeautifulSoup(html, 'html.parser')
                if self.config['hadis_lang'] == "English":
                    hadis = soup.find('div', class_ = 'english_hadith_full')
                    hadis_narrated = (hadis.find('div', class_ = 'hadith_narrated')).text
                    hadis_text = ((hadis.find('div', class_ = 'text_details')).findAll('p')[0]).text
                    await utils.answer(message=message, response=f"""<b>{hadis_narrated}</b>
{hadis_text}""")
                if self.config['hadis_lang'] == "Arabic":
                    hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                    await utils.answer(message=message, response=f"{hadis}")
                if self.config['hadis_lang'] == "Russian":
                    hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                    await self.invoke(peer=message.peer_id, command="tr", args=f"ru {hadis}")
            except ValueError:
                await utils.answer(message=message, response=self.strings('hadis_wrong'))

    @loader.command(
        ru_doc="<номер хадиса Сахих Аль-Бухари>",
        en_doc="<hadis number sahih Al-Bukhari>"
    )
    async def bukharicmd(self, message: Message):
        """<hadis number sahih Al-Bukhari>"""
        args = utils.get_args_raw(message)
        if args and args is not None:
            try:
                args = int(args)
                url = f"https://sunnah.com/bukhari:{args}"
                html = (requests.get(url)).text
                soup = BeautifulSoup(html, 'html.parser')
                if self.config['hadis_lang'] == "English":
                    try:
                        hadis = soup.find('div', class_ = 'english_hadith_full')
                        hadis_narrated = (hadis.find('div', class_ = 'hadith_narrated')).text
                        hadis_text = ((hadis.find('div', class_ = 'text_details')).findAll('p')[0]).text
                        await utils.answer(message=message, response=f"""<b>{hadis_narrated}</b>
{hadis_text}""")
                    except AttributeError:
                        await utils.answer(message=message, response=self.strings('hadis_wrong'))
                if self.config['hadis_lang'] == "Arabic":
                    try:
                        hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                        await utils.answer(message=message, response=f"{hadis}")
                    except AttributeError:
                        await utils.answer(message=message, response=self.strings('hadis_wrong'))
                if self.config['hadis_lang'] == "Russian":
                    try:
                        hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                        await self.invoke(peer=message.peer_id, command="tr", args=f"ru {hadis}")
                    except AttributeError:
                        await utils.answer(message=message, response=self.strings('hadis_wrong'))
            except ValueError:
                await utils.answer(message=message, response=self.strings('hadis_wrong'))
    @loader.command(
        ru_doc="<сура:аят>",
        en_doc="<surah:ayat>"
    )
    async def ayatcmd(self, message: Message):
    	"""<surah:ayat>"""
    	args = utils.get_args_raw(message)
    	pam = args.split(":")
    	if len(pam) <= 1:
    		await utils.answer(message=message, response = self.strings('ayat_wrong'))
    	if len(pam) == 2:
    		url = f"https://quran-online.ru/{args}"
    		html = (requests.get(url)).text
    		soup = BeautifulSoup(html, 'html.parser')
            try:
        		ayat = (((soup.findAll('dl', class_= 'dl-horizontal'))[6]).findAll('dd', class_ = 'ayat'))[0].text
        		await utils.answer(message=message, response=ayat)
            except IndexError:
                await utils.answer(message=message, response=self.strings('ayat_wrong'))
    	if len(pam) >= 3:
    		await utils.answer(message=message, response=self.strings('ayat_wrong'))

    async def watcher(self, message: Message):
        try:
            if getattr(message, "from_id", None) != self._tg_id and not self.config['only_me']:
                msg = (message.text).split(" ")
                if len(msg) == 2:
                    if msg[0] == '.ayat':
                        suraayat = (msg[1]).split(":")
                        if len(suraayat) == 2:
                            url = "https://quran-online.ru/" + msg[1]
                            html = (requests.get(url)).text
                            soup = BeautifulSoup(html, 'html.parser')
                            ayat = (((soup.findAll('dl', class_= 'dl-horizontal'))[6]).findAll('dd', class_ = 'ayat'))[0].text
                            await message.reply(ayat)
                    if msg[0] == ".bukhari":
                        hadis_number = (msg[1])
                        try:
                            hadis_number = int(hadis_number)
                            url = f"https://sunnah.com/bukhari:{hadis_number}"
                            html = (requests.get(url)).text
                            soup = BeautifulSoup(html, 'html.parser')
                            if self.config['hadis_lang'] == "English":
                                hadis = soup.find('div', class_ = 'english_hadith_full')
                                hadis_narrated = (hadis.find('div', class_ = 'hadith_narrated')).text
                                hadis_text = ((hadis.find('div', class_ = 'text_details')).findAll('p')[0]).text
                                await message.reply(f"""<b>{hadis_narrated}</b>
{hadis_text}""")
                            if self.config['hadis_lang'] == "Arabic":
                                hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                                await message.reply(hadis)
                            if self.config['hadis_lang'] == "Russian":
                                hadis = soup.find('div', class_ = "arabic_hadith_full arabic").text
                                await self.invoke(peer=message.peer_id, command="tr", args=f"ru {hadis}")
                        except:
                            pass
                if message.text == ".ramadan":
                    await message.reply(f"🎉 До Священного месяца Рамадан осталось: {day_to_ramadan()} дней!")
                if message.text.lower() == ".abdullah help":
                    await self.invoke(peer=message.peer_id, command="help", args="Abdullah")
        except:
            pass