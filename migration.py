from google.cloud import firestore
import json


firestore_db = firestore.Client.from_service_account_json('.streamlit/firestore_key.json', database='nekoconnect-dev-db')

# migrate users
local_file = 'data/nekoconnect_db_dev.json'

# load local file
with open(local_file, 'r') as f:
    data = json.load(f)

# iterate through data and upload to firestore, use phone number as id
for id, user in data['users'].items():
    firestore_id = user['phone_number']
    doc_ref = firestore_db.collection('users').document(firestore_id)
    user['tokens'] = 0
    doc_ref.set(user)
    print(f'uploaded {firestore_id}')

# migrate toy records
local_file = 'data/toy_record_db_dev.json'

# load local file
with open(local_file, 'r') as f:
    data = json.load(f)

machine_data = data['machines']
record_data = data['records']

# iterate through data and upload to firestore, use id as id
for id, record in machine_data.items():
    if 'doc_id' in record:
        del record['doc_id']
    machine_id = record['id']
    doc_ref = firestore_db.collection('machines').document(machine_id)
    doc_ref.set(record)
    print(f'uploaded {machine_id}')


for id, record in record_data.items():
    record_id = f'{record["date"]}#{record["machine_id"]}'
    doc_ref = firestore_db.collection('records').document(record_id)
    doc_ref.set(record)
    print(f'uploaded {record_id}')