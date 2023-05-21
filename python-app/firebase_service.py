from firebase_admin import credentials, initialize_app, storage

# Init firebase with your credentials
def upload(file):
    cred = credentials.Certificate("firebaseadminkey.json")
    initialize_app(cred, {'storageBucket': 'wropoznienia-a3395.appspot.com'})

    # Put your local file path 
    bucket = storage.bucket()
    blob = bucket.blob(file.split('/')[-1])
    blob.upload_from_filename(file)