import mainfile
from time import sleep
from firebase_admin import credentials, initialize_app, firestore
import firebase_service as fb
import getmpkdata as mpk
from datetime import datetime
import pandas as pd
import numpy as np
from geopy import distance

def calculate_delay(row):
    next_stop_time = datetime.strptime(row['next_stop_time'], "%Y-%m-%d %H:%M:%S")
    delay_seconds = max((current_day_time - next_stop_time).total_seconds(), 0)
    return delay_seconds

def match_best_from_all_stops(row):
    stop_ids = row['stops_ids'].split("/")
    stop_delays = [distance.geodesic((row['position_lat'], row['position_lon']), (stop_mapping[int(stop_id)]['stop_lat'], stop_mapping[int(stop_id)]['stop_lon'])).km for stop_id in stop_ids]
    stop_delays_temp = stop_delays.copy()

    min_delay = min(stop_delays_temp)
    stop_delays_temp.remove(min_delay)
    second_min_delay = min(stop_delays_temp)

    next_stop_index = max(stop_delays.index(min_delay), stop_delays.index(second_min_delay)) + 1

    if next_stop_index < len(stop_ids):
        return next_stop_index
    else:
        return 'end_of_trip'


    
cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com', 'databaseURL': 'https://wropoznienia-a3395.firebaseio.com/'})

firebase_db = firestore.client()

columns = ['unique_id', 'brigade_id', 'route_id', 'direction', 'position_lat', 'position_lon', 'stops_ids', 'stops_times', 'next_stop_id',
                             'next_stop_time', 'next_stop_lat', 'next_stop_lon', 'delay_seconds', 'distance']

data = pd.DataFrame(columns=columns)
h = 0

try:
    trips_df = pd.read_csv("data/trips.txt")
    stops_df = pd.read_csv("data/stops.txt")
except:
    mpk.get_schedules('https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip', './data/')
    trips_df = pd.read_csv("data/trips.txt")
    stops_df = pd.read_csv("data/stops.txt")

stop_mapping = stops_df.set_index('stop_id').loc[:, ['stop_lat', 'stop_lon']].to_dict(orient='index')

while True:
    current_day_time = datetime.now()
    response = mainfile.run(trips_df, stops_df, current_day_time)

    if response[1] == False:
        sleep(60)
        data = pd.DataFrame(columns=columns)
    else:
        new_data = response[0]

        if len(new_data) == 0:
            stop_times_df = pd.read_csv("data/stop_times.txt")
            mainfile.rare_data_upkeep(stop_times_df)
            fb.upload_file_to_storage('data/stops.txt')

        old_list = data['unique_id'].values.tolist()
        new_unique_list = new_data['unique_id'].values.tolist()
        new_list = list(set(new_unique_list).difference(old_list))
        gone_list = list(set(old_list).difference(new_unique_list))

        if len(new_list) > 0:
            new_data = new_data[(new_data['position_lat'].between(-90, 90)) & (new_data['position_lon'].between(-90, 90))]
            only_new_data = new_data.loc[new_data['unique_id'].isin(new_list)]

            only_new_data['next_stop_id'] = only_new_data.apply(lambda row: row['stops_ids'].split("/")[match_best_from_all_stops(row)] if match_best_from_all_stops(row) != 'end_of_trip' else 'end_of_trip', axis=1)
            only_new_data['next_stop_time'] = only_new_data.apply(lambda row: row['stops_times'].split("/")[match_best_from_all_stops(row)] if match_best_from_all_stops(row) != 'end_of_trip' else 'end_of_trip', axis=1)
            only_new_data = only_new_data[(only_new_data['next_stop_id'] != 'end_of_trip') | (only_new_data['next_stop_time'] != 'end_of_trip')]
            only_new_data['next_stop_lat'] = only_new_data['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lat'])
            only_new_data['next_stop_lon'] = only_new_data['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lon'])

            data = pd.concat((data, only_new_data)) # dodanie nowych pojazdów do DF

        data = data[~data['unique_id'].isin(gone_list)] # usunięcie pojazdów, które zakończyły trasę (ograniczenie DF tylko do tych, które nadal są raportowane)

        # merged_data = data.merge(new_data[['unique_id', 'position_lat', 'position_lon']], on='unique_id', how='left')
        # lat_list = merged_data['position_lat_y'].values.tolist()
        # lon_list = merged_data['position_lon_y'].values.tolist()
        # data['position_lat'] = lat_list
        # data['position_lon'] = lon_list
        
        position_lat_dict = new_data.set_index('unique_id')['position_lat'].to_dict()
        position_lon_dict = new_data.set_index('unique_id')['position_lon'].to_dict()

        data['position_lat'] = data['unique_id'].map(position_lat_dict)
        data['position_lon'] = data['unique_id'].map(position_lon_dict)

        data['distance'] = data.apply(lambda row: distance.geodesic((row['position_lat'], row['position_lon']), (row['next_stop_lat'], row['next_stop_lon'])).km if pd.notnull(row['next_stop_lat']) and pd.notnull(row['next_stop_lon']) else np.nan, axis=1)

        filtered_rows = data[data['distance'] <= 0.15]
        
        # Usunięcie pojazdów, które dojechały na ostatni przystanek
        filtered_rows['last_stop_id'] = filtered_rows['stops_ids'].str.split("/").str[-1]
        vehicles_to_remove = filtered_rows.loc[filtered_rows['last_stop_id'] == filtered_rows['next_stop_id']]
        vehicles_to_remove_list = vehicles_to_remove['unique_id'].values
        data = data[~data['unique_id'].isin(vehicles_to_remove_list)]

        
        # Aktualizacja kolumn dotyczących następnego przystanku
        filtered_rows = filtered_rows.loc[filtered_rows['last_stop_id'] != filtered_rows['next_stop_id']]
        if len(filtered_rows) > 0:
            filtered_rows['next_stop_id'] = filtered_rows.apply(lambda row: row['stops_ids'].split("/")[row['stops_ids'].split("/").index(row['next_stop_id']) + 1], axis=1)
            filtered_rows['next_stop_time'] = filtered_rows.apply(lambda row: row['stops_times'].split("/")[row['stops_ids'].split("/").index(row['next_stop_id'])], axis=1)
            filtered_rows['next_stop_lat'] = filtered_rows['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lat'])
            filtered_rows['next_stop_lon'] = filtered_rows['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lon'])

            data.update(filtered_rows)

        data['delay_seconds'] = data.apply(lambda row: calculate_delay(row), axis=1)

        data = data[data['delay_seconds'] <= 3600]

        h += 1

        data = data.drop_duplicates()


        try:
            print("Uploading file...")
            data.to_csv('data/vehicles_data.csv', encoding='utf-8-sig', index=False)
            data.to_excel('data/vehicles_data.xlsx', encoding='utf-8-sig', index=False)

            fb.upload_file_to_storage('data/vehicles_data.csv')
        except:
            pass
        
        sleep(10)
