# import time
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
    with requests.get(url) as response:
        print(4.1)
        # time.sleep(1)
        data = response.json()
        print(4.2)
        # Liczba stron wyszukiwania
        cycles = math.ceil(data['result']['total']/100)
        records = data['result']['records']  # Lista pojazdów MPK
    print(4.3)
    print(cycles)

    for i in range(1, cycles):
        url = f'https://www.wroclaw.pl/open-data/api/action/datastore_search?offset={i*100}&resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
        print(i)
        # time.sleep(1)
        with requests.get(url) as response_temp:
            data_temp = response_temp.json()
            records += data_temp['result']['records']
        

    return records

def get_schedules(url, destination='.'):
<<<<<<< HEAD
    http_response = urllib.request.urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
=======
    response = requests.get(url)
    zipfile = ZipFile(BytesIO(response.content))
>>>>>>> 0daeb35716c08af2b39696c466280c80a5646b7e
    zipfile.extractall(path=destination)