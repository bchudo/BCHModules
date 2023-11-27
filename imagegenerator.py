# meta developer: @bchmodules
# meta pic: https://0x0.st/HwtW.jpg
# meta banner: https://0x0.st/HwEW.jpg

from .. import loader, utils

import random
from contextlib import suppress
from telethon.tl.types import Message
import asyncio
import logging
from telethon.tl.functions.channels import JoinChannelRequest

logger = logging.getLogger(__name__)

@loader.tds
class ImageGeneratorMod(loader.Module):
	""""""
	strings = {
		"name": "ImageGenerator",
		"chatgpt_disabled": "❌ <b>ChatGPT in prompt generations disabled</b>",
		"chatgpt_enabled": "✅ <b>ChatGPT in prompt generations enabled</b>",
		"no_args": "❌ No arguments!",
		"generation": "<b>⏳ Generation . . .</b>\n\n<b>Prompt</b>: <i>{}</i>",
		"error": "❌ <b>Error!</b> <i>Check in PM with @YamiChat_bot</i>"
	}
	strings_ru = {
		"name": "ImageGenerator",
		"chatgpt_disabled": "❌ <b>ChatGPT в генерациях запроса выключен</b>",
		"chatgpt_enabled": "✅ <b>ChatGPT в генерациях запроса включен</b>",
		"no_args": "❌ Нет аргументов!",
		"generation": "<b>⏳ Генерация . . .</b>\n\n<b>Промпт</b>: <i>{}</i>",
		"error": "❌ <b>Ошибка!</b> <i>Смотрите ее в ЛС с @YamiChat_bot</i>"
	}

	def __init__(self):
		self.use_chatgpt = False

	async def client_ready(self, client, db):
		check = await self.client.get_messages("@YamiChat_bot", limit=1)
		self._client = client
		try:
			check[0]
		except IndexError:
			await self.client.send_message("@YamiChat_bot", "/start")
		yami_bot = await self.client.get_entity("t.me/YamiChat_bot")
		await utils.dnd(client=self.client, peer=yami_bot, archive=True)
		try:
			channels = [
				await self.client.get_entity("t.me/bchmodules"),
				await self.client.get_entity("t.me/YamiChannel")
			]
			await client(JoinChannelRequest(channels[0]))
			await client(JoinChannelRequest(channels[1]))
		except Exception as e:
			logger.error(f"Can't join channels\n{e}")

	@loader.command(ru_doc="использовать ChatGPT генерациях запроса? По умолчанию - нет.")
	async def usechatgptcmd(self, message: Message):
		"""Use ChatGPT in generation prompt? Default - no."""
		if self.use_chatgpt:
			self.use_chatgpt = False
			await utils.answer(message=message, response=self.strings("chatgpt_disabled"))
			return
		self.use_chatgpt = True
		await utils.answer(message=message, response=self.strings("chatgpt_enabled"))

	@loader.command(ru_doc="<prompt> сгенерировать изображение")
	async def imgcmd(self, message: Message):
		"""<prompt> generate image"""
		args = utils.get_args_raw(message)
		if not args:
			await utils.answer(message=message, response=self.strings("no_args"))
			return
		async with self.client.conversation("@YamiChat_bot") as conv:
			await utils.answer(message=message, response=self.strings("generation").format(args))
			prompt = ""
			if self.use_chatgpt:
				await conv.send_message(f"/ask дай мне промпт на английском языке, где {args}. без лишних \"да, конечно, вот твой промпт\", \"промпт:\" и т.д.")
				prompt = (await conv.get_response()).text
				lines = prompt.split("\n")
				for i in lines:
					if "Потрачено токенов" in i:
						lines.remove(i)
				prompt = "".join(lines)
			else:
				prompt = args
			await conv.send_message(f"/img {prompt}")
		while True:
			await asyncio.sleep(3)
			msgs = await self.client.get_messages("@YamiChat_bot", limit=1)
			if "Image for: " in msgs[0].text:
				await message.delete()
				break
			if "Ваш запрос похож на небезопасный" in msgs[0].text or "Ошибка!" in msgs[0].text:
				await utils.answer(message=message, response=self.strings("error"))
				return
		images_list = []
		images = await self.client.get_messages("@YamiChat_bot", limit=4)
		for i in images:
			if i.media is not None:
				images_list.append(i.media)
		reply = await message.get_reply_message()
		await self.client.send_file(
			message.peer_id,
			reply_to=reply.id if reply else None,
			file=images_list,
			caption= (images[0].text + "\n\nCreated by <b><a href=\"https://t.me/YamiChat_bot\">Yami</a></b>") if images[0].text else None,
			force_document=False
		)
