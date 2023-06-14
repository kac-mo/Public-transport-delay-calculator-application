from firebase_admin import storage
<<<<<<< HEAD

# Init firebase with your credentials
def upload(file):

    # Put your local file path 
=======
import pandas as pd

def upload_file_to_storage(filename):
>>>>>>> d0fbcf65fac8304e7a8b1bed17500f95e858b421
    bucket = storage.bucket()
    blob = bucket.blob(filename.split('/')[-1])
    blob.upload_from_filename(filename)


# def upload_df_to_database(df, doc_ref, firestore_client, existing_document_ids):
    # df.drop(['stops_ids', 'stops_times'], axis=1, inplace=True)
    # df.set_index('unique_id', drop=False, inplace=True)

    # batch = firestore_client.batch()  # Create a batch object

    # # Iterate over the DataFrame
    # for index, row in df.iterrows():
    #     document_data = row.to_dict()
    #     document_id = str(index)  # Convert the index to string if needed

    #     document_ref = doc_ref.document()

    #     if document_id in existing_document_ids:
    #         # Document already exists, update it
    #         batch.update(document_ref, document_data)
    #         existing_document_ids.remove(document_id)  # Remove ID from set
    #     else:
    #         # Document doesn't exist, add it
    #         batch.set(document_ref, document_data)

    # # Delete the remaining documents from Firestore
    # for doc_id in existing_document_ids:
    #     batch.delete(firestore_client.document(doc_id))

    # # Commit the batched writes
    # batch.commit()