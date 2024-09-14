import json
import tempfile
import os

import streamlit as st
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from st_files_connection import FilesConnection


class DB:
    def __init__(self):
        self.conn = st.connection('gcs', type=FilesConnection)
        db_dict = self.conn.read("nekoconnect-database/nekoconnect_db.json", input_format="json", ttl=0)
        self.db = TinyDB(storage=MemoryStorage)
        self.db.storage.read = lambda: db_dict
        self.users_table = self.db.table('users')

    def table(self, table_name):
        return self.db.table(table_name)

    def save(self):
        # Convert the database to a JSON string
        db_json = json.dumps(self.db.storage.read())

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            # Write the JSON string to the temporary file
            temp_file.write(db_json)
            temp_file.flush()

            # Use the put method to upload the file
            self.conn._instance.put(temp_file.name, "nekoconnect-database/nekoconnect_db.json")

        os.unlink(temp_file.name)