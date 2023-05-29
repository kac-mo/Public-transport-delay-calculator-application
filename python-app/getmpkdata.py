import requests
import math
from io import BytesIO
from zipfile import ZipFile
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_data():
    """
    Funkcja pobierająca i odpowiednio obrabiająca dane dotyczące pojazdów MPK z Wrocławskiego API

    Returns:
            records (list): lista pojazdów MPK
            cycles (int): liczba setek wyników
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    url = 'https://www.wroclaw.pl/open-data/api/action/datastore_search?resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
    with session.get(url) as response:
        print(4.1)
        # time.sleep(1)
        data = response.json()
        print(4.2)
        cycles = math.ceil(data['result']['total']/100) # Liczba stron wyszukiwania
        records = data['result']['records']  # Lista pojazdów MPK
    print(4.3)
    print(cycles)

    for i in range(1, cycles):
        url = f'https://www.wroclaw.pl/open-data/api/action/datastore_search?offset={i*100}&resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
        with session.get(url) as response_temp:
            data_temp = response_temp.json()
            records += data_temp['result']['records']
        
    return records

def get_schedules(url, destination='.'):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(url)
    zipfile = ZipFile(BytesIO(response.content))
    zipfile.extractall(path=destination)