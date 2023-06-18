import mainfile
from time import sleep
import firebase_service as fb
from firebase_admin import credentials, initialize_app, firestore
import getmpkdata as mpk
from datetime import datetime
import pandas as pd
import numpy as np
from geopy import distance

cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com', 'databaseURL': 'https://wropoznienia-a3395.firebaseio.com/'})

firebase_db = firestore.client()

data = pd.DataFrame(columns=['unique_id', 'brigade_id', 'route_id', 'direction', 'position_lat', 'position_lon', 'stops_ids', 'stops_times', 'next_stop_id',
                             'next_stop_time', 'next_stop_lat', 'next_stop_lon', 'delay_seconds', 'distance'])
h = 0

try:
    trips_df = pd.read_csv("data/trips.txt")
    stops_df = pd.read_csv("data/stops.txt")
except:
    mpk.get_schedules('https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip', './data/')
    trips_df = pd.read_csv("data/trips.txt")
    stops_df = pd.read_csv("data/stops.txt")

stop_mapping = stops_df.set_index('stop_id').loc[:, ['stop_lat', 'stop_lon']].to_dict(orient='index')

columns = ['unique_id', 'brigade_id', 'route_id', 'direction', 'position_lat', 'position_lon', 'stops_ids', 'stops_times', 'next_stop_id',
                             'next_stop_time', 'next_stop_lat', 'next_stop_lon', 'delay_seconds', 'distance']

while True:
    current_day_time = datetime.now()
    response = mainfile.run(trips_df, stops_df, current_day_time)
    new_data = response[0]

    if response[1] == False:
        sleep(60)
        data = pd.DataFrame(columns=['unique_id', 'brigade_id', 'route_id', 'direction', 'position_lat', 'position_lon', 'stops_ids', 'stops_times', 'next_stop_id',
                             'next_stop_time', 'next_stop_lat', 'next_stop_lon', 'delay_seconds', 'distance'])
    else:
        # print("Uploading file...")
        # fb.upload("data/vehicles_data.csv")
        new_unique_list = new_data['unique_id'].values.tolist()
        new_list = list(set(new_unique_list).difference(data['unique_id'].values.tolist()))
        gone_list = list(set(data['unique_id'].values.tolist()).difference(new_unique_list))

        if len(new_list) > 0:
            only_new_data = new_data.loc[new_data['unique_id'].isin(new_list)].copy()
            only_new_data['next_stop_id'] = 'NP'
            
            if len(data) == 0:
                not_precise_list = only_new_data['unique_id'].values.tolist()
            else:
                only_new_data['next_stop_id'] = only_new_data['stops_ids'].apply(lambda x: x.split("/")[1])
                only_new_data['next_stop_time'] = only_new_data['stops_times'].apply(lambda x: x.split("/")[1])
                only_new_data['next_stop_lat'] = only_new_data['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lat'])
                only_new_data['next_stop_lon'] = only_new_data['next_stop_id'].map(lambda x: stop_mapping[int(x)]['stop_lon'])

            data = pd.concat((data, only_new_data)) # dodanie nowych pojazdów do DF

        data['distance'] = np.nan
        data = data[~data['unique_id'].isin(gone_list)] # usunięcie pojazdów, które zakończyły trasę (ograniczenie DF tylko do tych, które nadal są raportowane)
        
        for index, row in data.iterrows():
            unique_id = row['unique_id']

            try:
                row['position_lat'] = new_data.loc[new_data['unique_id'] == str(unique_id), 'position_lat'].values[0]
                row['position_lon'] = new_data.loc[new_data['unique_id'] == str(unique_id), 'position_lon'].values[0]
            except:
                row['position_lat'] = new_data.loc[new_data['unique_id'] == str(unique_id), 'position_lat']
                row['position_lon'] = new_data.loc[new_data['unique_id'] == str(unique_id), 'position_lon']
            
            if not row.isna()['position_lat'] and row['position_lat'] <= 90 and row['position_lat'] >= -90:  
                if row['next_stop_id'] == 'NP':
                    np_last_stop_id = int(row['stops_ids'].split("/")[-1])
                    np_last_stop_pos = (stop_mapping[np_last_stop_id]['stop_lat'], stop_mapping[np_last_stop_id]['stop_lon'])

                    if distance.geodesic((row['position_lat'], row['position_lon']), np_last_stop_pos).km <= 0.1:
                        gone_list.append(row['unique_id'])
                else:              
                    now_distance = distance.geodesic((row['position_lat'], row['position_lon']), (row['next_stop_lat'], row['next_stop_lon'])).km

                    row['distance'] = float(now_distance)
                    
                    if now_distance <= 0.1:
                        print(f"VEHICLE {row['unique_id']} HAS REACHED ITS STOP")
                        temp_stop_ids_list = row['stops_ids'].split("/")
                        temp_index = temp_stop_ids_list.index(row['next_stop_id']) + 1
                        if temp_index == (len(temp_stop_ids_list)):
                            gone_list.append(row['unique_id'])
                        
                        if temp_index < len(temp_stop_ids_list):
                            row['next_stop_id'] = temp_stop_ids_list[temp_index]
                            row['next_stop_time'] = row['stops_times'].split("/")[temp_index]
                            row['next_stop_lat'] = stop_mapping[int(row['next_stop_id'])]['stop_lat']
                            row['next_stop_lon'] = stop_mapping[int(row['next_stop_id'])]['stop_lon']
                    
                    delay_seconds = (current_day_time - datetime.strptime(row['next_stop_time'], "%Y-%m-%d %H:%M:%S")).total_seconds()
                    row['delay_seconds'] = float(delay_seconds)

            data_dict = dict(zip(columns, row))


            for col_name in columns:
                data.loc[data['unique_id'] == data_dict['unique_id'], col_name] = data_dict[col_name]
        
        h += 1

        data = data.drop_duplicates()
        data = data[~data['unique_id'].isin(gone_list)] # usunięcie pojazdów, które zakończyły trasę (ograniczenie DF tylko do tych, które nadal są raportowane)

        try:
            print("Uploading file...")
            # data_copy.drop(['stops_ids', 'stops_times'], axis=1, inplace=True)
            data.to_csv('data/vehicles_data.csv', encoding='utf-8-sig', index=False)

            fb.upload_file_to_storage('data/vehicles_data.csv')
        except:
            pass

        if len(data) == 0:
            mpk.get_schedules('https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip', './data/')
            stop_times_df = pd.read_csv("data/stop_times.txt")
            mainfile.rare_data_upkeep(stop_times_df)
            fb.upload_file_to_storage('data/stops.txt')
        
        print(data)
        sleep(2)
