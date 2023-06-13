import requests
import math
from io import BytesIO
from zipfile import ZipFile

def get_data():
    """
    Funkcja pobierająca i odpowiednio obrabiająca dane dotyczące pojazdów MPK z Wrocławskiego API

    Returns:
            records (list): lista pojazdów MPK
            cycles (int): liczba setek wyników
    """
    url = 'https://www.wroclaw.pl/open-data/api/action/datastore_search?resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
    obj_dict = requests.get(url).json()
    # Liczba stron wyszukiwania
    cycles = math.ceil(obj_dict['result']['total']/100)
    records = obj_dict['result']['records']  # Lista pojazdów MPK

    for i in range(1, cycles):
        url = f'https://www.wroclaw.pl/open-data/api/action/datastore_search?offset={i*100}&resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
        obj_dict_temp = requests.get(url).json()
        records += obj_dict_temp['result']['records']

    return records

def get_schedules(url, destination='.'):
    http_response = requests.get(url, stream=True)
    zipfile = ZipFile(BytesIO(http_response.content))
    zipfile.extractall(path=destination)