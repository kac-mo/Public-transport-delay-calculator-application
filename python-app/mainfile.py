import pandas as pd
from geopy import distance
from datetime import datetime, timedelta
import getmpkdata as mpk
import textmanipulations as tedit

def rare_data_upkeep(stop_times_df):
    trip_id_list = []
    trip_stop_times = []
    trip_stop_ids = []

    date_today = str(datetime.now()).split(" ")[0]  # Dzisiejsza data w postaci string
    date_tomorrow = str(datetime.now() + timedelta(days=1)).split(" ")[0] # Jutrzejsza data w postaci string

    grouped_df = stop_times_df.groupby('trip_id')

    trip_stop_times_str = grouped_df['arrival_time'].apply(lambda x: '/'.join(tedit.match_datetime_midnight_formatting(time, date_today, date_tomorrow) for time in x)).reset_index(drop=True)
    trip_stop_ids_str = grouped_df['stop_id'].apply(lambda x: '/'.join(str(stop) for stop in x)).reset_index(drop=True)

    unique_trip_ids = grouped_df.groups.keys()
    trip_id_list.extend(unique_trip_ids)
    trip_stop_times.extend(trip_stop_times_str)
    trip_stop_ids.extend(trip_stop_ids_str)

    # j = 0

    # while j < len(stop_times_df):
    #     trip_id = stop_times_df['trip_id'][j]
    #     trip_stop_times_str = ""
    #     trip_stop_ids_str = ""
    #     if trip_id_list.count(trip_id) == 0:
    #         while stop_times_df['trip_id'][j] == trip_id:
    #             trip_stop_ids_str += f"{stop_times_df['stop_id'][j]}/"
    #             trip_stop_times_str += f"{tedit.match_datetime_midnight_formatting(stop_times_df['arrival_time'][j], date_today, date_tomorrow)}/"
    #             j += 1
    #             if j == len(stop_times_df):
    #                 break

    #         trip_stop_times_str = trip_stop_times_str[:-1]
    #         trip_stop_ids_str = trip_stop_ids_str[:-1]
    #         trip_id_list.append(trip_id)
    #         trip_stop_times.append(trip_stop_times_str)
    #         trip_stop_ids.append(trip_stop_ids_str)

    #         if j == len(stop_times_df):
    #             break

    #         if str(round((j / (len(stop_times_df)) * 100), 0)) != past_pct:
    #             past_pct = str(round((j / (len(stop_times_df)) * 100), 0))
    #             print(f"Progress: {past_pct}%")

    stop_times_start_end_data = {'trip_id': trip_id_list, 'trip_stop_ids': trip_stop_ids, 'trip_stop_times': trip_stop_times}
    trip_info_df = pd.DataFrame(stop_times_start_end_data)
    trip_info_df.to_csv('data/trip_info.csv', encoding='utf-8-sig', index=False)
    print("data upkeep: done.")

def get_vehicles_data(line_brigade_df, trips_df, stops_df, trip_info_df, current_service_id, current_day_time):
    brigade_ids = []
    route_ids = []
    directions = []
    current_lat = []
    current_lon = []
    stops_ids = []
    stops_times = []

    trip_ids_list = trip_info_df['trip_id'].values.tolist()
    stops_ids_list = trip_info_df['trip_stop_ids'].values.tolist()
    stops_times_list = trip_info_df['trip_stop_times'].values.tolist()

    now_trips_df = trips_df[
        (trips_df['route_id'].isin(line_brigade_df['Numer_Linii'])) &
        (trips_df['brigade_id'].isin(line_brigade_df['brigade_id'])) &
        (trips_df['service_id'] == current_service_id)
    ].copy()

    for i in range(len(line_brigade_df)):
        # try:
            temp_df = now_trips_df[
                (now_trips_df['route_id'] == str(line_brigade_df['Numer_Linii'][i])) &
                (now_trips_df['brigade_id'] == int(line_brigade_df['brigade_id'][i]))
            ].copy()
            
            # Aktualna lokalizacja pojazdu
            current_vehicle_lat = line_brigade_df['pozycja_szerokosc'][i]
            current_vehicle_lon = line_brigade_df['pozycja_dlugosc'][i]

            possible_trips_list = []
            if len(list(temp_df['trip_id'])) > 0:
                possible_trip_id_list = list(temp_df['trip_id'])
                possible_route_id = list(temp_df['route_id'])[0]

                for trip_id in possible_trip_id_list:
                    index = trip_ids_list.index(trip_id)
                    possible_stop_ids = stops_ids_list[index]
                    possible_stops_times = stops_times_list[index]
                    possible_start_time = datetime.strptime(
                        possible_stops_times.split('/')[0], "%Y-%m-%d %H:%M:%S")  # Czas startu danego tripa
                    possible_end_time = datetime.strptime(
                        possible_stops_times.split('/')[-1], "%Y-%m-%d %H:%M:%S")  # Czas zakończenia danego tripa
                    possible_trip_length = possible_end_time - \
                        possible_start_time  # Rozkładowy czas trwania trasy
                    time_since_trip_started = possible_end_time - \
                        current_day_time  # Czas od rozkładowego wyruszenia
                    
                    # Sprawdzam możliwe tripy, na których może znajdować się pojazd
                    if current_day_time > possible_start_time and current_day_time < possible_end_time:
                        possible_trips_list.append(
                            (trip_id, possible_route_id, possible_start_time, possible_end_time, possible_trip_length, time_since_trip_started, possible_stop_ids, possible_stops_times))

                    # Jeśli możliwych tripów było > 1, wówczas dokonuję weryfikacji
                    if len(possible_trips_list) > 1:
                        # try:
                            possible_trips_list = solve_double_possible_paths(
                                possible_trips_list, stops_df, trip_info_df, current_vehicle_lat, current_vehicle_lon)
                        # except:
                        #     # print(
                        #     #     "- - - -\nUNRESOLVED ERROR, FLIPPING A COIN ON VEHICLE MATCH...")
                        #     possible_trips_list = [possible_trips_list[0]]

                if len(possible_trips_list) > 0:
                    route_ids.append(possible_route_id)
                    directions.append(
                        temp_df.loc[(temp_df['trip_id'] == possible_trips_list[0][0])].iloc[0, 3])
                    current_lat.append(current_vehicle_lat)
                    current_lon.append(current_vehicle_lon)
                    brigade_ids.append(line_brigade_df['brigade_id'][i])
                    stops_ids.append(possible_trips_list[0][6])
                    stops_times.append(possible_trips_list[0][7])
        # except:
        #     print("Oof")
        #     pass

    return (route_ids, directions, current_lat, current_lon, stops_ids, stops_times, brigade_ids)

def solve_double_possible_paths(possible_trips_list, stops_df, trip_info_df, current_lat, current_lon):

    stops1 = trip_info_df.loc[(trip_info_df['trip_id'] == possible_trips_list[0][0]), 'trip_stop_ids'].values[0].split("/")  # ID przystanków 1. możliwej trasy
    stops2 = trip_info_df.loc[(trip_info_df['trip_id'] == possible_trips_list[1][0]), 'trip_stop_ids'].values[0].split("/")  # ID przystanków 2. możliwej trasy

    # Procentowy progress czasowy 1
    time_on_trip_pct1 = possible_trips_list[0][5] / possible_trips_list[0][4]
    # Procentowy progress czasowy 2
    time_on_trip_pct2 = possible_trips_list[1][5] / possible_trips_list[1][4]

    first_stop_pos1 = (stops_df.loc[(stops_df['stop_id'] == int(
        stops1[0]))].iloc[0, 3], stops_df.loc[(stops_df['stop_id'] == int(stops1[0]))].iloc[0, 4])
    final_stop_pos1 = (stops_df.loc[(stops_df['stop_id'] == int(
        stops1[-1]))].iloc[0, 3], stops_df.loc[(stops_df['stop_id'] == int(stops1[-1]))].iloc[0, 4])

    first_stop_pos2 = (stops_df.loc[(stops_df['stop_id'] == int(
        stops2[0]))].iloc[0, 3], stops_df.loc[(stops_df['stop_id'] == int(stops2[0]))].iloc[0, 4])
    final_stop_pos2 = (stops_df.loc[(stops_df['stop_id'] == int(
        stops2[-1]))].iloc[0, 3], stops_df.loc[(stops_df['stop_id'] == int(stops2[-1]))].iloc[0, 4])

    current_distance_from_first_stop1 = distance.geodesic(
        (current_lat, current_lon), first_stop_pos1).km
    current_distance_from_first_stop2 = distance.geodesic(
        (current_lat, current_lon), first_stop_pos2).km

    trip_length_1 = distance.geodesic(first_stop_pos1, final_stop_pos1).km
    trip_length_2 = distance.geodesic(first_stop_pos2, final_stop_pos2).km

    current_trip_distance_pct1 = current_distance_from_first_stop1 / \
        trip_length_1  # Procentowy progress odległościowy 1
    current_trip_distance_pct2 = current_distance_from_first_stop2 / \
        trip_length_2  # Procentowy progress odległościowy 2

    # print(f"TRIP 1: {time_on_trip_pct1}, {current_trip_distance_pct1}")
    # print(f"TRIP 2: {time_on_trip_pct2}, {current_trip_distance_pct2}")
    trip_pct_diff1 = abs(current_trip_distance_pct1 - time_on_trip_pct1)
    trip_pct_diff2 = abs(current_trip_distance_pct2 - time_on_trip_pct2)

    if trip_pct_diff1 <= trip_pct_diff2:
        possible_trips_list = [possible_trips_list[0]]
    else:
        possible_trips_list = [possible_trips_list[1]]

    return possible_trips_list

def create_vehicles_data_csv(line_brigade_df, trips_df, stops_df, current_service_id, current_day_time):                     
    """
    Funkcja tworząca plik trip_id_time_windows.csv, który posiada informację o oknie czasowym dla każdego z tripów

    Parameters:
        stop_times_df (pd.DataFrame): pandas DataFrame zawierający informację o czasach przyjazdu pojazdów MPK na przystanki
    """

    trip_info_df =  pd.read_csv("data/trip_info.csv")

    route_ids, directions, current_lat, current_lon, stops_ids, stops_times, brigade_ids = get_vehicles_data(
        line_brigade_df, trips_df, stops_df, trip_info_df, current_service_id, current_day_time)
    
    unique_ids = []
    for i in range(len(brigade_ids)):
        unique_ids.append(str(route_ids[i]) + '_' + str(brigade_ids[i])) # Unikalne ID per pojazd

    present_data = {'unique_id': unique_ids, 'brigade_id': brigade_ids, 'route_id': route_ids, 'direction': directions,
            'position_lat': current_lat, 'position_lon': current_lon, 'stops_ids': stops_ids, 'stops_times': stops_times}
    present_data_df = pd.DataFrame(present_data)

    # print("File creation completed")
    return present_data_df

def create_line_brigade_df(records, current_day_time):
    brigade_id_list = []
    lane_number_list = []
    update_time_list = []
    longitude_list = []
    latitude_list = []

    for elem in records:
        if elem['Nazwa_Linii'] != '' and elem['Nazwa_Linii'] != 'None':
            if elem['Brygada'] != '' and elem['Brygada'] != 'None':
                update_time = datetime.strptime(
                    elem['Data_Aktualizacji'][:19], "%Y-%m-%d %H:%M:%S")
                # Sprawdzam ile czasu mija między teraz a ostatnią aktualizacją pojazdu
                time_difference = abs(current_day_time - update_time)
                if time_difference.seconds < 300:
                    # Pobieram id brygady - unikalne ID per pojazd per linia
                    elem['brigade_id'] = elem['Brygada'][-2:]
                    # Usuwam zera, które czasem pojawiają się przy zbieraniu ostatnich dwóch elementów z 'Brygady'
                    try:
                        brigade_id_no_zeros = int(tedit.delete_zeros_at_beginning(
                            elem['brigade_id']))
                        # Elementy pod nowy DF
                        brigade_id_list.append(brigade_id_no_zeros)
                        lane_number_list.append(elem['Nazwa_Linii'])
                        update_time_list.append(update_time)
                        longitude_list.append(elem['Ostatnia_Pozycja_Dlugosc'])
                        latitude_list.append(elem['Ostatnia_Pozycja_Szerokosc'])
                    except:
                        pass
                    

    line_brigade_data = {'Numer_Linii': lane_number_list, 'brigade_id': brigade_id_list,
                         'update_time': update_time_list, 'pozycja_dlugosc': longitude_list, 'pozycja_szerokosc': latitude_list}
    # Nowy dataframe z numerem linii i id brygady
    return (pd.DataFrame(line_brigade_data))

def run(trips_df, stops_df, current_day_time):
    print('Creating time-related variables...')
    # Dzień tygodnia jako int // 0 - Monday, 6 - Sunday
    current_week_day = datetime.weekday(current_day_time)
    # service_id: {3 : sob, 4 : nie, 6 : pon/wt/sr/czw, 8 : pt}
    week_day_service_id_dict = {0: 6, 1: 6, 2: 6, 3: 6, 4: 6, 5: 3, 6: 4}
    # Service id do matchowania odpowiedniego trip id
    current_service_id = week_day_service_id_dict[current_week_day]

    print('Getting data from schedules, MPK API...')

    records = mpk.get_data()
    print('Matching data & attempting to create .csv...')
    line_brigade_df = create_line_brigade_df(records, current_day_time)
    if len(line_brigade_df) > 0:
        vehicles_data = create_vehicles_data_csv(line_brigade_df, trips_df, stops_df, current_service_id, current_day_time)
        return(vehicles_data, True)
    else:
        print('API is broken... :(')
        return(False, False)