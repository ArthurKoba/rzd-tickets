from asyncio import sleep, get_running_loop
from aiogram import Bot
from time import time

from rzd_api import RZDApi
from rzd_models import TrainFilter, Train


class Logic:
    def __init__(
            self,
            trains_filters: list[TrainFilter],
            bot: Bot,
            tg_admin_id: int,
            time_between_check: int = 60,
            timeout: int = 5
    ):
        self.__api = RZDApi()
        self.__bot = bot
        self.__tg_admin_id = tg_admin_id
        self.__trains_filters = trains_filters
        self.loop_task = None
        self.is_started = False
        self.__time_between_check = time_between_check
        self.__timeout = timeout
        self.__last_update = 0
        self.__mem = {}

    async def check(self) -> list[Train] | None:
        updates: list[Train] = []
        for train_filter in self.__trains_filters:
            trains = await self.__api.get_trains(train_filter)
            if trains is None:
                return None
            if self.__mem.get(id(train_filter)) is None:
                self.__mem.update({id(train_filter): {}})
            train_filter_memory = {}
            for train in trains:
                train_filter_memory.update({train.number: train.total_place_quantity})
                if self.__mem.get(id(train_filter)).get(train.number) == train.total_place_quantity:
                    continue
                updates.append(train)
            self.__mem.update({id(train_filter): train_filter_memory})

            await sleep(self.__timeout)
        self.__last_update = time()
        return updates

    async def start(self):
        if self.is_started:
            return print("Already Started")
        self.is_started = True
        loop = get_running_loop()
        loop.create_task(self.__loop())

    async def stop(self):
        self.is_started = False
        await self.loop_task

    async def send_start_notification(self, trains: list[Train]):
        text = "На данный момент ситуация следующая:\n"
        for train in trains:
            text += "[{} | {} -> {} | {}] - мест: {}\n".format(
                train.number,
                train.origin_station,
                train.destination_station,
                train.get_datetime(),
                train.total_place_quantity
            )
        await self.__bot.send_message(self.__tg_admin_id, text)
        print(text)

    async def send_updated_notification(self, trains: list[Train]):
        text = "Изменение состояния наличия билетов:\n"
        for train in trains:
            text += "[{}  | {} -> {} | {}] - Мест: {}\n".format(
                train.number,
                train.origin_station,
                train.destination_station,
                train.get_datetime(),
                train.total_place_quantity
            )
        await self.__bot.send_message(self.__tg_admin_id, text)
        print(text)

    async def __loop(self):
        print("Start logic")
        results = await self.check()
        if results:
            await self.send_start_notification(results)
        self.is_started = True
        while self.is_started:
            if time() - self.__last_update <= self.__time_between_check:
                await sleep(0.5)
                continue
            results = await self.check()
            if results:
                await self.send_updated_notification(results)
        print("Stop logic")
