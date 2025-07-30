import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime
import pytz

API_TOKEN = "8199710253:AAEO-Es0AIkuAS0H19Z3QHF2sfQSG58tcaI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

night_mode_enabled = False
creator_id = None
chat_id = None


@dp.message_handler(commands=["on"])
async def enable_night_mode(message: types.Message):
    global night_mode_enabled, creator_id, chat_id
    if message.chat.type not in ["supergroup", "group"]:
        return await message.reply("Эту команду можно использовать только в группе.")
    
    creator_id = message.from_user.id
    chat_id = message.chat.id
    night_mode_enabled = True
    await message.reply("✅ Ночной режим ВКЛЮЧЕН.")


@dp.message_handler(commands=["off"])
async def disable_night_mode(message: types.Message):
    global night_mode_enabled
    night_mode_enabled = False
    await message.reply("❌ Ночной режим ВЫКЛЮЧЕН.")


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    text = (
        "📖 Помощь по боту:\n\n"
        "/on – включить ночной режим\n"
        "/off – выключить ночной режим\n\n"
        "ℹ️ С 00:00 до 06:00 (по Киеву) бот будет "
        "автоматически отключать возможность писать всем, кроме создателя группы."
    )
    await message.reply(text)


async def night_mode_task():
    global night_mode_enabled, creator_id, chat_id
    kiev_tz = pytz.timezone("Europe/Kiev")

    while True:
        if night_mode_enabled and creator_id and chat_id:
            now = datetime.now(kiev_tz)
            try:
                if 0 <= now.hour < 6:
                    members = await bot.get_chat_administrators(chat_id)
                    for member in members:
                        if member.user.id != creator_id:
                            await bot.restrict_chat_member(
                                chat_id,
                                member.user.id,
                                permissions=types.ChatPermissions(can_send_messages=False)
                            )
                else:
                    members = await bot.get_chat_administrators(chat_id)
                    for member in members:
                        await bot.restrict_chat_member(
                            chat_id,
                            member.user.id,
                            permissions=types.ChatPermissions(can_send_messages=True)
                        )
            except Exception as e:
                print("Ошибка:", e)

        await asyncio.sleep(60)


async def on_startup(_):
    asyncio.create_task(night_mode_task())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
