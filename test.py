import urllib.request
import json
import math

url = 'https://www.wroclaw.pl/open-data/api/action/datastore_search?resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
obj = urllib.request.urlopen(url)
obj_dict = json.loads(obj.read().decode('utf-8'))
cycles = math.ceil(obj_dict['result']['total']/100) # Number of search sites
records = obj_dict['result']['records'] # List of MPK vehicles

for i in range(1, cycles):
    url = f'https://www.wroclaw.pl/open-data/api/action/datastore_search?offset={i*100}&resource_id=17308285-3977-42f7-81b7-fdd168c210a2'
    obj_temp = urllib.request.urlopen(url)
    obj_dict_temp = json.loads(obj_temp.read().decode('utf-8'))
    records += obj_dict_temp['result']['records']


# - - - - - TUTAJ SIĘ KOŃCZY NAJWAŻNIEJSZA CZĘŚĆ KODU - - - - - 
# records stanowi listę elementów słownikowych każdego pojazdu MPK
# ponizej kod, ktory tworzy 'brigade_id', ktore sie pokrywa z brigade id z pliku
# trips.txt. Trzeba tutaj wyczyścić elementy, których nazwa_linii == '' (ale to juz sam sie pobaw i ogarnij)
for elem in records:
    elem['brigade_id'] = elem['Brygada'][-2:]
    if elem['Nazwa_Linii'] not in elem['Brygada'][:-2]:
        print(elem)