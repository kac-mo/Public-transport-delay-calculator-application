import urllib.request
import json
import math
import pandas as pd
import re
from datetime import datetime

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

def delete_zeros_at_beginning(input):
    regex = "^0+(?!$)"
    output = re.sub(regex, "", input)
    return output

current_day_time = datetime.now()
print(current_day_time)

# ZBIERZ ID BRYGADY (2 ostatnie cyfry)
brigade_id_list = []
lane_number_list = []
for elem in records:
    if elem['Nazwa_Linii'] != '' and elem['Nazwa_Linii'] != 'None':
        if elem['Brygada'] != '' and elem['Brygada'] != 'None':
            update_time = datetime.strptime(elem['Data_Aktualizacji'][:19], "%Y-%m-%d %H:%M:%S")
            time_difference = abs(current_day_time - update_time) # Sprawdzam ile czasu mija między teraz a ostatnią aktualizacją pojazdu
            if time_difference.seconds > 300:
                elem['brigade_id'] = elem['Brygada'][-2:]
                brigade_id_no_zeros = delete_zeros_at_beginning(elem['brigade_id']) # Usuwam zera, które czasem pojawiają się przy zbieraniu ostatnich dwóch elementów z 'Brygady'
                brigade_id_list.append(brigade_id_no_zeros)
                lane_number_list.append(elem['Nazwa_Linii'])
                #print(brigade_id_no_zeros, elem['Nazwa_Linii'], elem['Brygada'])

line_brigade_data = {'Numer_Linii': lane_number_list, 'brigade_id': brigade_id_list}
line_brigade_df = pd.DataFrame(line_brigade_data) # Nowy dataframe z numerem linii i id brygady

trips_df = pd.read_csv("data/trips.csv")

for i in range(len(line_brigade_df)):
    # Jeśli numer linii i id brygady w rzędzie w trips_df jest taki sam jak w danym rzędzie line_brigade_df to go wydrukuj
    print(trips_df.loc[(trips_df['route_id'] == line_brigade_df['Numer_Linii'][i]) & (trips_df['brigade_id'] == int(line_brigade_df['brigade_id'][i]))])