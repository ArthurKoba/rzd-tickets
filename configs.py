from datetime import date
from os import getenv
from dotenv import load_dotenv

load_dotenv()

bot_token = getenv("RZD_TICKETS_BOT_TOKEN")
tg_admin_id = 593084007

trains_filter_data = [
    {
        "origin": "2064055",
        "destination": "2014130",
        "departure_date": date(2023, 9, 1)
    },
    {
        "origin": "2064055",
        "destination": "2014130",
        "departure_date": date(2023, 9, 2)
    }
]
