import mainloop
import time
import firebase_service as fb
from firebase_admin import credentials, initialize_app

cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})
old_tracking_list = []
while True:
    response = mainloop.run()
    data = response[0]
    if response[1] == False:
        time.sleep(60)
    else:
        print("Uploading file...")
        fb.upload("data/vehicles_data.csv")
        tracking_list = []
        for i in range(len(data)):
            unique_id = str(data.loc[i, 'route_id']) + str(data.loc[i, 'brigade_id'])
            
