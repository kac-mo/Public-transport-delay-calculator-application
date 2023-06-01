import mainloop2 as mainloop
import time
import firebase_service as fb
from firebase_admin import credentials, initialize_app

cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})
tracking_list = []
unprecise_tracking_list = []

while True:
    response = mainloop.run()
    data = response[0]
    if response[1] == False:
        time.sleep(60)
        tracking_list = []
    else:
        print("Uploading file...")
        fb.upload("data/vehicles_data.csv")
        now_unique_list = data['unique_id'].values.tolist()
        new_list = list(set(now_unique_list).difference(tracking_list))
        gone_list = list(set(tracking_list).difference(now_unique_list))

        if tracking_list == []:
            unprecise_tracking_list += new_list

        tracking_list += new_list
        for elem in gone_list:
            try:
                tracking_list.remove(elem)
                unprecise_tracking_list.remove(elem)
            except:
                pass
        
            
