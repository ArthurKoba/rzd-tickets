from aiohttp import ClientSession
from asyncio import get_running_loop
from json import load, dump

from rzd_models import Train, TrainFilter
from configs import proxy


class RZDApi:
    __url = "https://ticket.rzd.ru/apib2b/p/Railway/V1/Search/TrainPricing"

    def __init__(self, session: ClientSession = None):
        self.__session = session or ClientSession()

    def __del__(self):
        loop = get_running_loop()
        loop.create_task(self.__session.close())

    async def get_trains(self, train_filter: TrainFilter) -> list[Train] | None:
        try:
            response = await self.__session.post(self.__url, data=train_filter.get_json_to_request(), proxy=proxy)
            if response.status != 200:
                return print(f"error. status code: {response.status}")
            data = await response.json()
            error = data.get("errorInfo")
            if not error:
                return Train.parse_trains(data)
            print(f"[Error {error.get('Code')}] - {error.get('Message')}")
        except Exception as e:
            print(f"Request error: {e}")
        # with open("test.json", mode="w", encoding="utf-8") as f:
        #     dump(data, fp=f)
        # with open("test.json", mode="r", encoding="utf-8") as f:
        #     data = load(f)
        #     return Train.parse_trains(data)
