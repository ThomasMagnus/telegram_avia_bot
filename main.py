import telebot
import json
import re
from typing import Dict
import requests

from dateutil.parser import parse


class Cities(telebot.custom_filters.SimpleCustomFilter):
    key = 'city'

    def __init__(self, file: str, city: str):
        self.file = file
        self.cities_from_to: Dict[str, dict] = {}
        self.city = city

    def _get_cities(self) -> dict:
        with open(self.file, 'r', encoding='utf-8') as file:
            return json.loads(file.read())

    def get_city_dict(self) -> dict:
        city: list[str] = self.city.lower().split('/')
        city_from: str = city[0]
        city_to: str = city[1]
        print(city)
        for item in self._get_cities():
            if '-'.join(re.findall(r'\w+', str(item['name']))).lower() == city_from.lower() or \
                    ' '.join(re.findall(r'\w+', str(item['name']))).lower() == city_from.lower():
                self.cities_from_to['city_from'] = item
            if '-'.join(re.findall(r'\w+', str(item['name']))).lower() == city_to.lower() or \
                    ' '.join(re.findall(r'\w+', str(item['name']))).lower() == city_to.lower():
                self.cities_from_to['city_to'] = item
        return self.cities_from_to


class Tickets:

    def __init__(self, token: str, city: str, route: str, route_date: str) -> None:
        self.city = city
        self.cities = Cities('cities.json', self.city).get_city_dict()
        self.date: Dict[str, str] = {}
        self.token: str = token
        self.url: str = 'https://api.travelpayouts.com/aviasales/v3/prices_for_dates'
        self.route = route
        self.route_date = route_date

    def get_tickets(self) -> dict:
        session = requests.Session()
        print(self.cities)
        if self.route == 'Да':
            date = self.route_date.split('-')
            self.date['date_go']: str = parse(date[0], dayfirst=True).strftime('%Y-%m-%d')
            self.date['date_back']: str = parse(date[1], dayfirst=True).strftime("%Y-%m-%d")

            self.url += f'?origin={self.cities["city_from"]["code"]}&destination={self.cities["city_to"]["code"]}' \
                        f'&currency=rub&departure_at={self.date["date_go"]}&return_at=' \
                        f'{self.date["date_back"]}&sorting=price&direct=true&limit=10&token={self.token}'

        elif self.route == 'Нет':

            self.date['date_go'] = parse(self.route_date, dayfirst=True).strftime("%Y-%m-%d")
            self.url += f'?origin={self.cities["city_from"]["code"]}&destination={self.cities["city_to"]["code"]}' \
                        f'&currency=rub&departure_at={self.date["date_go"]}' \
                        f'&sorting=price&direct=true&limit=10&token={self.token}'
        headers = {
            "X-Access-Token": self.token
        }

        result: json = session.get(self.url, headers=headers)

        return result.json()


class Data:
    city: str = None
    date: str = None
    route: str = None
