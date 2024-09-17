from typing import Optional
from dataclasses import dataclass
from tinydb import Query
from toy_record_db import DB
from io import BytesIO
import streamlit as st




@dataclass
class Record:
    machine_id: str
    date: str
    coins_in: int
    toys_payout: int


@dataclass
class Machine:
    id: str
    name: str
    location: str
    status: str
    notes: Optional[str] = None
    image: Optional[str] = None   # path to image

@st.cache_data
def get_image_by_path(path, _db):
    image = _db.download_file(path)
    return image


class Manager:
    def __init__(self, env):
        self.db = DB(env)
        self.machines_table = self.db.table('machines')
        self.records_table = self.db.table('records')

    def create_machine(self, machine: Machine, image: BytesIO):
        n_machine = len(self.get_all_machines()) + 1
        machine.id = f"m{n_machine}"
        # upload image to blob storage
        image_path = f"images/machines/{machine.id}.jpg"
        self.db.upload_file(image, image_path, compress=True)
        machine.image = image_path
        self.machines_table.insert(machine.__dict__)
        self.db.save()

    def get_all_machines(self):
        return self.machines_table.all()
    
    def get_image_by_machine_id(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        path = machine['image']
        image = get_image_by_path(path, self.db)
        return image

    def get_machine_by_id(self, machine_id):
        return self.machines_table.get(Query().id == machine_id)

    def update_machine(self, machine_id, machine: Machine):
        self.machines_table.upsert(machine.__dict__, Query().id == machine_id)
        self.db.save()

    def delete_machine(self, machine_id):
        self.machines_table.remove(Query().id == machine_id)
        self.db.save()

    def create_record(self, record: Record):
        self.records_table.insert(record.__dict__)
        self.db.save()

    def get_all_records(self):
        return self.records_table.all()
