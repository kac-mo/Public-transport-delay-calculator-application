import pandas as pd

stop_times_df = pd.read_csv("data/stop_times.txt")

trip_id_list = []
trip_start_time_list = []
trip_end_time_list = []
i = 0
while i < len(stop_times_df):
    if trip_id_list.count(stop_times_df['trip_id'][i]) == 0:
        trip_start_time = stop_times_df['arrival_time'][i]
        j = i
        while stop_times_df['trip_id'][i] == stop_times_df['trip_id'][j]:
            j += 1
            if j == len(stop_times_df):
                break
        trip_end_time = stop_times_df['arrival_time'][j-1]
        trip_id_list.append(stop_times_df['trip_id'][i])
        trip_start_time_list.append(trip_start_time)
        trip_end_time_list.append(trip_end_time)
        i = j
        if j == len(stop_times_df):
            break
        print("check: " + str(i))

stop_times_start_end_data = {'trip_id': trip_id_list, 'trip_start_time': trip_start_time_list, 'trip_end_time': trip_end_time_list}
stop_times_start_end_df = pd.DataFrame(stop_times_start_end_data)
stop_times_start_end_df.to_csv('poopy.csv')
print("poopy check")