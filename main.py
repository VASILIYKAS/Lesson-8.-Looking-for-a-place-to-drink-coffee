import json
import requests
import folium
import os
from dotenv import load_dotenv
from geopy import distance
from flask import Flask


def coffe_data():
    """Загружает данные о кофейнях из указанного файла JSON."""
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_content = my_file.read()
    coffee_list = json.loads(file_content)
    return coffee_list


def fetch_coordinates(apikey, address):
    """Получает координаты места по его названию с использованием API Яндекс.Карт."""
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_user_location(apikey):
    """Запрашивает у пользователя его местоположение и возвращает координаты."""
    location = input('Где вы находитесь?: ')
    user_location = fetch_coordinates(apikey, location)
    return user_location


def nearest_cafes(coffee_list, user_location):
    """Создает список ближайших кофеен с расстоянием до них."""
    coffe_new_list = []
    for i in range(len(coffee_list)):
        coffe_dict = dict()
        coordinates = coffee_list[i]['geoData']['coordinates']
        coffe_dict['title'] = coffee_list[i]['Name']
        coffe_dict['latitude'] = coffee_list[i]['Latitude_WGS84']
        coffe_dict['longitude'] = coffee_list[i]['Longitude_WGS84']
        user_coordinates = user_location[::-1]
        coffee_coordinates = coordinates[::-1]
        calculated_distance = distance.distance(user_coordinates, coffee_coordinates).km
        coffe_dict['distance'] = calculated_distance
        coffe_new_list.append(coffe_dict)
    return coffe_new_list


def get_coffe_min(coff):
    """Извлекает расстояние до кофейни из словаря"""
    return coff['distance']


def sort(coffe_new_list):
    """Сортирует список кофеен по расстоянию и возвращает 5 ближайших"""
    near_coffe = sorted(coffe_new_list, key=get_coffe_min)
    coffe_name = near_coffe[:5]  # Делаем срез по первым 5 кафе
    return coffe_name


def create_map(coffe_name, user_location):
    """Создает карту с отмеченными ближайшими кофейнями и текущим местоположением пользователя."""
    longitude, latitude = user_location
    m = folium.Map([latitude, longitude], zoom_start=15)

    # Добавляем маркер для текущего местоположения
    folium.Marker(
        location=[latitude, longitude],
        tooltip='Вы здесь',
        popup=f'Ш:{latitude}\nД:{longitude}',
        icon=folium.Icon(color="red"),
    ).add_to(m)

    # Добавляем маркеры для ближайших кофеен
    for i in range(0, 5):
        folium.Marker(
            location=[coffe_name[i]['latitude'], coffe_name[i]['longitude']],
            tooltip=coffe_name[i]['title'],
            popup=f'До кофейни {round(coffe_name[i]["distance"], 2)} км',
            icon=folium.Icon(color="blue"),
        ).add_to(m)

    m.save("coffee.html")


def open_map():
    """Читает и возвращает содержимое HTML файла"""
    with open('coffee.html', encoding='utf-8') as file:
        return file.read()


# Запускаем сайт
def start_web_service():
    """Запускает веб-сервис для отображения карты кофеен."""
    app = Flask(__name__)
    app.add_url_rule('/', 'Coffe map', open_map)
    app.run('0.0.0.0')


def main():
    load_dotenv()
    coffee_list = coffe_data()
    apikey = os.getenv('API_KEY')
    user_location = get_user_location(apikey)
    coffe_new_list = nearest_cafes(coffee_list, user_location)
    coffe_name = sort(coffe_new_list)
    create_map(coffe_name, user_location)
    open_map()
    start_web_service()


if __name__ == '__main__':
    main()
