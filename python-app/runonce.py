import mainloop2 as mainloop
from firebase_admin import credentials, initialize_app
import firebase_service as fb

# cred = credentials.Certificate("firebaseadminkey.json")
# initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})

# response = mainloop.run()
# if response:
#     fb.upload("data/vehicles_data.csv")

list1 = [1, 2, 3, 4, 5, 6]
list2 = [1, 2, 5, 7]

new_list = list(set(set(list1).difference(list2)).union(set(list2).difference(list1)))

try:
    new_list.remove(7)
except:
    pass

print(new_list)