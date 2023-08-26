from asyncio import new_event_loop, sleep

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from logic import Logic
from rzd_models import TrainFilter
from configs import bot_token, tg_admin_id, trains_filter_data


async def main():
    session = AiohttpSession()
    bot = Bot(bot_token, session=session)
    trains_filter = [TrainFilter(**data) for data in trains_filter_data]
    logic = Logic(trains_filters=trains_filter, bot=bot, tg_admin_id=tg_admin_id, timeout=1, time_between_check=60)
    await bot.send_message(tg_admin_id, "Скрипт запущен!")
    await logic.start()

    while logic.is_started:
        await sleep(1)
    await session.close()


if __name__ == '__main__':
    loop = new_event_loop()
    loop.create_task(main())
    loop.run_forever()


