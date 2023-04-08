import urllib.request
import json
import math
import pandas as pd
import re
from geopy import distance
from datetime import datetime, timedelta

def get_MPK_data():
    """
    Funkcja pobierająca i odpowiednio obrabiająca dane dotyczące pojazdów MPK z Wrocławskiego API

    Returns:
            records (list): lista pojazdów MPK
            cycles (int): liczba setek wyników
    """

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

    return records

def delete_zeros_at_beginning(input):
    """
    Funkcja usuwająca wszystkie '0', które znajdują się na początku stringu

    Parameters:
            input (str): modyfikowany string
    Returns:
            output (str): zmodyfikowany string
    """
    regex = "^0+(?!$)"
    output = re.sub(regex, "", input)
    return output

def match_datetime_midnight_formatting(time, date_today, date_tomorrow):
    """
    Funkcja modyfikująca format stringu daty po północy, by odpowiadał temu z biblioteki datetime

    Parameters:
            time (str): HH:MM:SS string
            date_today (str): string dzisiejszej daty
            date_tomorrow (str): string jutrzejszej daty
    Returns:
            output (str): data w prawidłowym formacie
    """
    if int(time[:2]) >= 24:
        time = "0" + str(int(time[:2]) - 24) + time[2:]
        output = f"{date_tomorrow} {time}"
    else:
        output = f"{date_today} {time}"
    return output

def create_trips_time_windows_csv(stop_times_df):
    """
    Funkcja tworząca plik trip_id_time_windows.csv, który posiada informację o oknie czasowym dla każdego z tripów

    Parameters:
            stop_times_df (pd.DataFrame): pandas DataFrame zawierający informację o czasach przyjazdu pojazdów MPK na przystanki
    """
    trip_id_list = []
    trip_start_time_list = []
    trip_end_time_list = []
    trip_first_last_stop_ids_list = []

    past_pct = "" # Zmienna służaca temu, żeby każda wartość % była wydrukowana tylko raz
    date_today = str(datetime.now()).split(" ")[0] # Dzisiejsza data w postaci string
    date_tomorrow = str(datetime.now() + timedelta(days=1)).split(" ")[0] # Jutrzejsza data w postaci string

    j = 0
    trip_start_time = match_datetime_midnight_formatting(stop_times_df['arrival_time'][j], date_today, date_tomorrow) # Modyfikacja formatu daty o północy, by odpowiadał temu z biblioteki datetime
    trip_stop_ids = [stop_times_df['stop_id'][j]]

    while j < len(stop_times_df):
        trip_id = stop_times_df['trip_id'][j]
        if trip_id_list.count(trip_id) == 0:
            while stop_times_df['trip_id'][j] == trip_id:
                j += 1
                if j == len(stop_times_df):
                    break
            
            trip_end_time = match_datetime_midnight_formatting(stop_times_df['arrival_time'][j-1], date_today, date_tomorrow)
            trip_stop_ids.append(stop_times_df['stop_id'][j-1])

            start_date = datetime.strptime(trip_end_time, "%Y-%m-%d %H:%M:%S") # Początek trasy jako data
            end_date = datetime.strptime(trip_end_time, "%Y-%m-%d %H:%M:%S") # Koniec trasy jako data

            # Sprawdzanie, czy trasa kończy się po północy
            if end_date < start_date:
                print(start_date, end_date)
                # Jeśli tak, odpowiednio zmieniany jest trip_end_time
                trip_end_time = f"{date_tomorrow} {stop_times_df['arrival_time'][j-1]}"

            trip_id_list.append(trip_id)
            trip_start_time_list.append(trip_start_time)
            trip_end_time_list.append(trip_end_time)
            trip_first_last_stop_ids_list.append(trip_stop_ids)


            if j == len(stop_times_df):
                break

            trip_stop_ids = [stop_times_df['stop_id'][j]]
            trip_start_time = match_datetime_midnight_formatting(stop_times_df['arrival_time'][j], date_today, date_tomorrow)

            if str(round((j / (len(stop_times_df)) * 100), 0)) != past_pct:
                print(f"trip_id_time_windows_progress: {str(round((j / (len(stop_times_df)) * 100), 0))}%")
                past_pct = str(round((j / (len(stop_times_df)) * 100), 0))

    stop_times_start_end_data = {'trip_id': trip_id_list, 'trip_start_time': trip_start_time_list, 'trip_end_time': trip_end_time_list, 'trip_stop_ids': trip_first_last_stop_ids_list}
    stop_times_start_end_df = pd.DataFrame(stop_times_start_end_data)
    stop_times_start_end_df.to_csv('data/trip_id_time_windows.csv')
    print("trip_id_time_windows_progress: file creation completed")

trip_id_time_windows_df = pd.read_csv("data/trip_id_time_windows.csv")
trips_df = pd.read_csv("data/trips.txt")
stop_times_df = pd.read_csv("data/stop_times.txt")
stops_df = pd.read_csv("data/stops.txt")

current_day_time = datetime.now()
current_week_day = datetime.weekday(current_day_time) # Dzień tygodnia jako int // 0 - Monday, 6 - Sunday

records = get_MPK_data()

brigade_id_list = []
lane_number_list = []
update_time_list = []
longitude_list = []
latitude_list = []

for elem in records:
    if elem['Nazwa_Linii'] != '' and elem['Nazwa_Linii'] != 'None':
        if elem['Brygada'] != '' and elem['Brygada'] != 'None':
            update_time = datetime.strptime(elem['Data_Aktualizacji'][:19], "%Y-%m-%d %H:%M:%S")
            time_difference = abs(current_day_time - update_time) # Sprawdzam ile czasu mija między teraz a ostatnią aktualizacją pojazdu
            if time_difference.seconds < 300:
                elem['brigade_id'] = elem['Brygada'][-2:] # Pobieram id brygady - unikalne ID per pojazd per linia
                brigade_id_no_zeros = delete_zeros_at_beginning(elem['brigade_id']) # Usuwam zera, które czasem pojawiają się przy zbieraniu ostatnich dwóch elementów z 'Brygady'
                
                # Elementy pod nowy DF
                brigade_id_list.append(brigade_id_no_zeros)
                lane_number_list.append(elem['Nazwa_Linii'])
                update_time_list.append(update_time)
                longitude_list.append(elem['Ostatnia_Pozycja_Dlugosc'])
                latitude_list.append(elem['Ostatnia_Pozycja_Szerokosc'])

line_brigade_data = {'Numer_Linii': lane_number_list, 'brigade_id': brigade_id_list, 'update_time': update_time_list, 'pozycja_dlugosc': longitude_list, 'pozycja_szerokosc' : latitude_list}
line_brigade_df = pd.DataFrame(line_brigade_data) # Nowy dataframe z numerem linii i id brygady

# service_id: {3 : sob, 4 : nie, 6 : pon/wt/sr/czw, 8 : pt}
week_day_service_id_dict = {0 : 6, 1 : 6, 2 : 6, 3 : 6, 4 : 8, 5 : 3, 6 : 4}
current_service_id = week_day_service_id_dict[current_week_day] # Service id do matchowania odpowiedniego trip id


# Aktualizacja formatu godziny na przystankach:
for i in range(10):
    scheduled_departure_time = f'{str(current_day_time.date())} {stop_times_df.at[i, "departure_time"]}'

# create_trips_time_windows_csv(stop_times_df)

for i in range(len(line_brigade_df)):
    # Każda iteracja i drukuje dataframe możliwych trip_ids dla pojazdu danej linii o danym brigade_id.
    # Skoro jest to ten konkretny pojazd, jego aktualna godzina będzie mogła znajdować się tylko w jednym z przedziałów czasowych tripów
    # A więc mając brigade_id i route_id i aktualny czas jestesmy w stanie okreslic, jaki jest trip_id pojazdu, a zatem dopasowac
    # Odpowiedni rozklad jazdy ESSA
    
    # temp_df = trips_df.loc[(trips_df['route_id'] == line_brigade_df['Numer_Linii'][i]) & (trips_df['brigade_id'] == int(line_brigade_df['brigade_id'][i])) & (trips_df['service_id'] == 6) & (trips_df['direction_id'] == 1)]
    try:
        temp_df = trips_df.loc[(trips_df['route_id'] == line_brigade_df['Numer_Linii'][i]) & (trips_df['brigade_id'] == int(line_brigade_df['brigade_id'][i])) & (trips_df['service_id'] == current_service_id)]
        current_vehicle_pos = (line_brigade_df['pozycja_szerokosc'], line_brigade_df['pozycja_dlugosc']) # Aktualna lokalizacja pojazdu
        
        possible_trips_list = []
        if len(list(temp_df['trip_id'])) > 0:
            possible_trip_id_list = list(temp_df['trip_id'])
            possible_route_id = list(temp_df['route_id'])[0]

            for trip_id in possible_trip_id_list:
                time_window_df = trip_id_time_windows_df.loc[(trip_id_time_windows_df['trip_id'] == trip_id)]
                possible_start_time = datetime.strptime(time_window_df.iloc[0,2], "%Y-%m-%d %H:%M:%S") # Czas startu danego tripa
                possible_end_time = datetime.strptime(time_window_df.iloc[0,3], "%Y-%m-%d %H:%M:%S") # Czas zakończenia danego tripa
                possible_trip_length = possible_end_time - possible_start_time # Rozkładowy czas trwania trasy
                time_since_trip_started = possible_end_time - current_day_time # Czas od rozkładowego wyruszenia
                if current_day_time > possible_start_time and current_day_time < possible_end_time: # Sprawdzam możliwe tripy, na których może znajdować się pojazd
                    possible_trips_list.append((trip_id, possible_route_id, possible_start_time, possible_end_time, possible_trip_length, time_since_trip_started))

            if len(possible_trips_list) > 1: # Jeśli możliwych tripów było > 1, wówczas dokonuję weryfikacji
                trip1_df = trips_df.loc[trips_df['trip_id'] == possible_trips_list[0][0]]
                trip2_df = trips_df.loc[trips_df['trip_id'] == possible_trips_list[1][0]]
                stops1 = trip_id_time_windows_df.loc[(trip_id_time_windows_df['trip_id'] == possible_trips_list[0][0])].iloc[0,4].replace("'", "").replace(" ", "")[1:-1].split(",")
                stops2 = trip_id_time_windows_df.loc[(trip_id_time_windows_df['trip_id'] == possible_trips_list[1][0])].iloc[0,4].replace("'", "").replace(" ", "")[1:-1].split(",")
                time_on_trip_pct1 = possible_trips_list[0][5] / possible_trips_list[0][4]
                time_on_trip_pct2 = possible_trips_list[1][5] / possible_trips_list[1][4]

                first_stop_pos1 = (stops_df.loc[(stops_df['stop_id'] == int(stops1[0]))].iloc[0,3], stops_df.loc[(stops_df['stop_id'] == int(stops1[0]))].iloc[0,4])
                first_stop_pos2 = (stops_df.loc[(stops_df['stop_id'] == int(stops2[0]))].iloc[0,3], stops_df.loc[(stops_df['stop_id'] == int(stops2[0]))].iloc[0,4])
                final_stop_pos1 = (stops_df.loc[(stops_df['stop_id'] == int(stops1[1]))].iloc[0,3], stops_df.loc[(stops_df['stop_id'] == int(stops1[1]))].iloc[0,4])
                final_stop_pos2 = (stops_df.loc[(stops_df['stop_id'] == int(stops2[1]))].iloc[0,3], stops_df.loc[(stops_df['stop_id'] == int(stops2[1]))].iloc[0,4])

                print((time_on_trip_pct1, time_on_trip_pct2))
                print("- - - - -")
                possible_next_stop_id_1 = 1
            # https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    
    except:
        print('- - - - - -\nERROR')
        print(line_brigade_df['brigade_id'][i])
        print("- - - - - -")

current_distance = distance.distance(current_vehicle_pos, final_stop_pos1).km
print("done")