import mainfile
from firebase_admin import credentials, initialize_app
import firebase_service as fb
import pandas as pd
from datetime import datetime
import getmpkdata as mpk
from time import sleep

cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})

# current_day_time = datetime.now()
# trips_df = pd.read_csv("data/trips.txt")
# stops_df = pd.read_csv("data/stops.txt")

# response = mainfile.run(trips_df, stops_df, current_day_time)
# if response:

while True:
    fb.upload_file_to_storage("data/vehicles_data.csv")
    sleep(2)
    print('sent')

# mpk.get_schedules('https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip', './data/')
# stop_times_df = pd.read_csv("data/stop_times.txt")
# mainfile.rare_data_upkeep(stop_times_df)
# print("done")


# list1 = [1, 2, 3, 4, 5, 6]
# list2 = [1, 2, 5, 7]

# new_list = list(set(set(list1).difference(list2)).union(set(list2).difference(list1)))

# try:
#     new_list.remove(7)
# except:
#     pass

# print(new_list)
