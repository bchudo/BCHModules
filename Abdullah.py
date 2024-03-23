# meta developer: @bchmodules
# meta pic: https://0x0.st/HwtW.jpg
# meta banner: https://0x0.st/Hwtv.jpg

from .. import loader, utils

from telethon.tl.types import Message
import aiohttp

@loader.tds
class AbdullahMod(loader.Module):
    """Раб Аллаха."""

    strings = {
        "name": "Abdullah"
    }
    quran_url = "http://api.alquran.cloud/v1/ayah/{sura}:{ayat}/ru.kuliev"
    hadith_url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{lang}-{edition}/{number}.json"
    
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
                "rus",
                "Язык, на котором будут хадисы",
                validator = loader.validators.Choice(["rus", "ara", "eng"])
            )
        )
    
    @loader.watcher("only_messages", regex=r"\.ayat \d+:\d+$")
    async def quran_watcher(self, message: Message):
        sura, ayat = message.text.split()[1].split(":")
        if message.from_id != self.tg_id:
            await message.reply((await self.get_ayat(int(sura), int(ayat))))
        else:
            await utils.answer(message, (await self.get_ayat(int(sura), int(ayat))))
    
    @loader.watcher("only_messages", regex=r"\.muslim \d+$")
    async def muslim_watcher(self, message: Message):
        number = int(message.text.split()[1])
        if message.from_id != self.tg_id:
            await message.reply((await self.get_hadith(self.config["hadis_lang"], "muslim", number)))
        else:
            await utils.answer(message, (await self.get_hadith(self.config["hadis_lang"], "muslim", number)))
    
    @loader.watcher("only_messages", regex=r"\.abudawud \d+$")
    async def abudawud_watcher(self, message: Message):
        number = int(message.text.split()[1])
        if message.from_id != self.tg_id:
            await message.reply((await self.get_hadith(self.config["hadis_lang"], "abudawud", number)))
        else:
            await utils.answer(message, (await self.get_hadith(self.config["hadis_lang"], "abudawud", number)))
    
    @loader.watcher("only_messages", regex=r"\.bukhari \d+$")
    async def bukhari_watcher(self, message: Message):
        number = int(message.text.split()[1])
        if message.from_id != self.tg_id:
            await message.reply((await self.get_hadith(self.config["hadis_lang"], "bukhari", number)))
        else:
            await utils.answer(message, (await self.get_hadith(self.config["hadis_lang"], "bukhari", number)))
    
    async def get_ayat(self, sura: int, ayat: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.quran_url.format(sura=sura, ayat=ayat)) as response:
                data = await response.json()
                if data['status'] != "OK":
                    return "Что-то пошло не так..."
                return (
                    f"<emoji document_id=5373098009640836781>📚</emoji> Перевод: {data['data']['edition']['name']}\n" \
                    f"<emoji document_id=5240004029769064410>❗️</emoji> Сура {data['data']['surah']['name']}, всего аятов в суре: {data['data']['surah']['numberOfAyahs']}\n" \
                    f"<emoji document_id=5240426478457332312>#️⃣</emoji> Страница №{data['data']['page']}\n\n" \
                    f"{data['data']['text']}"
                )

    async def get_hadith(self, lang: str, edition: str, number: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.hadith_url.format(lang=lang, edition=edition, number=number)) as response:
                if response.status != 200:
                    return "Что-то пошло не так..."
                data = await response.json()
                hadith_text =  (
                    f"<emoji document_id=5373098009640836781>📚</emoji> Название книги: {data['metadata']['name']}, глава {data['metadata']['section'][list(data['metadata']['section'])[0]]} под номером {list(data['metadata']['section'])[0]}\n"
                    f"<emoji document_id=5240426478457332312>#️⃣</emoji> Русский номер хадиса: {data['hadiths'][0]['hadithnumber']}, арабский номер хадиса: {data['hadiths'][0]['arabicnumber']}\n\n" \
                    f"<emoji document_id=5249277199168579635>📌</emoji> <b>{data['hadiths'][0]['text']}</b>"
                )
                if grades := data['hadiths'][0]['grades']:
                    hadith_text += "\n\n<emoji document_id=5248949999970036769>📣</emoji> Учёные об этом хадисе:\n"
                    hadith_text += ",\n".join([f"<i><emoji document_id=5370724846936267183>🤔</emoji> {grade['name']} поставил оценку {grade['grade']}</i>" for grade in grades])
                    # for grade in grades:
                    #     hadith_text += ",\n".join(f"<i><emoji document_id=5370724846936267183>🤔</emoji> {grade['name']} поставил оценку {grade['grade']}</i>")
                return hadith_text
    
    
    async def ayatcmd(self, message):
        """<сура:аят> - аят из корана"""
    
    async def bukharicmd(self, message):
        """<номер хадиса> - хадис Бухари"""
    
    async def muslimcmd(self, message):
        """<номер хадиса> - хадис Муслима"""
    
    async def abudawudcmd(self, message):
        """<номер хадиса> - хадис Абу Дауда"""