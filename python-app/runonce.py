import mainloop
from firebase_admin import credentials, initialize_app
import firebase_service as fb

cred = credentials.Certificate("firebaseadminkey.json")
initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})

response = mainloop.run()
if response:
    fb.upload("data/vehicles_data.csv")