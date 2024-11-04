import json
import requests
import folium
import os
from dotenv import load_dotenv
from geopy import distance


# Открываем файл с кофешками Москвы
def coffe_data():
    with open("coffee.json", "r") as my_file:
        file_content = my_file.read()
    coffee_list = json.loads(file_content)
    return coffee_list


# Функция получения координат места по его названию
def fetch_coordinates(apikey, address):
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


# Просим пользователя указать место, что бы получить координаты
def place(apikey):
    location = input('Где вы находитесь?: ')  # Примеры: Внуково, Серпуховская, Красная площадь
    our_location = fetch_coordinates(apikey, location)
    return our_location


# Создание нового словаря для дальнейшего использования
def nearest_cafes(coffee_list, our_location):
    coffe_new_list = []
    for i in range(len(coffee_list)):
        coffe_dict = dict()
        coordinates = coffee_list[i]['geoData']['coordinates']
        coffe_dict['title'] = coffee_list[i]['Name']
        coffe_dict['latitude'] = coffee_list[i]['Latitude_WGS84']
        coffe_dict['longitude'] = coffee_list[i]['Longitude_WGS84']
        coffe_dict['distance'] = distance.distance(our_location[::-1], coordinates[::-1]).km
        coffe_new_list.append(coffe_dict)
    return coffe_new_list


# Сортируем кофешки по удалённости
def get_coffe_min(coff):
    return coff['distance']


def sort(coffe_new_list):
    near_coffe = sorted(coffe_new_list, key=get_coffe_min)
    coffe_name = near_coffe[:5]  # Делаем срез по первым 5 кафе
    return coffe_name


# Отмечаем на карте 5 ближайших к нам кофешек и расстояние до них
def map(coffe_name, our_location):
    longitude, latitude = our_location
    m = folium.Map([latitude, longitude], zoom_start=15)
    folium.Marker(
        location=[latitude, longitude],
        tooltip='Вы здесь',
        popup=f'Ш:{latitude}\nД:{longitude}',
        icon=folium.Icon(color="red"),
    ).add_to(m)

    for i in range(0, 5):
        folium.Marker(
            location=[coffe_name[i]['latitude'], coffe_name[i]['longitude']],
            tooltip=coffe_name[i]['title'],
            popup=f'До кофейни {round(coffe_name[i]['distance'], 2)} км',
            icon=folium.Icon(icon="cloud"),
        ).add_to(m)

    m.save("coffee.html")  # Сохраняем карту "coffee.html"

    os.startfile('coffee.html')  # Открываем карту "coffee.html"


def main():
    load_dotenv()
    coffee_list = coffe_data()
    apikey = os.getenv('API_KEY')
    our_location = place(apikey)
    coffe_new_list = nearest_cafes(coffee_list, our_location)
    coffe_name = sort(coffe_new_list)
    map(coffe_name, our_location)


if __name__ == '__main__':
    main()
