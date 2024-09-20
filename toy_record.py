from typing import Optional
from dataclasses import dataclass
from tinydb import Query
from toy_record_db import DB
from io import BytesIO
import streamlit as st
import uuid
from dataclasses import field
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class Record:
    machine_id: str
    coins_in: int
    toys_payout: int
    param_strong_strength: float
    param_medium_strength: float
    param_weak_strength: float
    param_award_interval: int
    param_mode: str = ''
    notes: Optional[str] = None
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Machine:
    name: str
    location: str
    status: str
    param_strong_strength: float
    param_medium_strength: float
    param_weak_strength: float
    param_award_interval: int
    param_mode: str = ''
    id: str = None
    notes: Optional[str] = None
    image: Optional[str] = None   # path to image

    def get_params(self):
        """Summary of the machine parameters"""
        try:
            results = f'{self.param_strong_strength}, {self.param_medium_strength}, {self.param_weak_strength} | {self.param_award_interval}, {self.param_mode}'
            return results
        except Exception as e:
            return None

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
        logger.info("create_machine")
        logger.info(machine)
        if image is not None:
            # upload image to blob storage
            image_path = f"images/machines/{machine.id}.jpg"
            self.db.upload_file(image, image_path, compress=True)
            machine.image = image_path
        
        self.machines_table.upsert(machine.__dict__, Query().id == machine.id)
        self.db.save()

    def get_all_machines(self):
        return self.machines_table.all()

    def get_all_machines_obj(self):
        machines = self.get_all_machines()
        res = []
        for machine in machines:
            if 'doc_id' in machine:
                del machine['doc_id']
            machine_obj = Machine(**machine)
            res.append(machine_obj)

        return res

    def get_image_by_machine_id(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        path = machine['image']
        if path is None:
            return None
        image = get_image_by_path(path, self.db)
        return image

    def get_machine_by_id(self, machine_id):
        return self.machines_table.get(Query().id == machine_id)

    def get_machine_obj_by_id(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        if 'doc_id' in machine.keys():
            del machine['doc_id']
        return Machine(**machine)

    def update_machine(self, machine_id, machine):
        res = self.machines_table.upsert(machine, Query().id == machine_id)
        self.db.save()

    def delete_machine(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        self.machines_table.remove(Query().id == machine_id)
        if machine['image'] is not None:
            self.db.delete_file(machine['image'])
        self.db.save()

    def create_record(self, record: Record):
        self.records_table.upsert(record.__dict__, (Query().machine_id == record.machine_id) & (Query().date == record.date))

        # update machine parameters
        machine_id = record.machine_id
        machine = self.get_machine_by_id(machine_id)
        machine['param_strong_strength'] = record.param_strong_strength
        machine['param_medium_strength'] = record.param_medium_strength
        machine['param_weak_strength'] = record.param_weak_strength
        machine['param_award_interval'] = record.param_award_interval
        machine['param_mode'] = record.param_mode
        self.update_machine(machine_id, machine)   # db saved

    def get_all_records(self):
        return self.records_table.all()

    def get_all_records_df(self):
        records = self.get_all_records()
        df = pd.DataFrame(records)
        return df

    def get_records_by_machine_id(self, machine_id):
        keys = ['date', 'coins_in', 'toys_payout', 'param_strong_strength', 'param_medium_strength', 'param_weak_strength', 'param_award_interval', 'param_mode', 'notes']
        records = self.records_table.search(Query().machine_id == machine_id)
        df = pd.DataFrame(records)
        # sort by date
        df = df.sort_values(by='date', ascending=True)

        return df[keys]

    def calculate_machine_payout_rate(self, machine_id):
        records = self.get_records_by_machine_id(machine_id)
        processed_records = []
        # daily payout rate
        records['date'] = pd.to_datetime(records['date'])
        records_sorted = records.sort_values(by='date', ascending=True)
        for i in range(1, records.shape[0]):
            yesterday_coins_in = records_sorted.iloc[i-1]['coins_in']
            yesterday_toys_payout = records_sorted.iloc[i-1]['toys_payout']
            today_coins_in = records_sorted.iloc[i]['coins_in']
            today_toys_payout = records_sorted.iloc[i]['toys_payout']
            
            if today_coins_in < yesterday_coins_in:
                yesterday_coins_in = 0
            if today_toys_payout < yesterday_toys_payout:
                yesterday_toys_payout = 0

            coins_diff = today_coins_in - yesterday_coins_in
            toys_diff = today_toys_payout - yesterday_toys_payout
            if coins_diff == 0 or toys_diff == 0:
                daily_payout_rate = 0
            else:
                daily_payout_rate = coins_diff / toys_diff

            processed_records.append({
                'date': records_sorted.iloc[i]['date'],
                'daily_coins_in': coins_diff,
                'daily_toys_payout': toys_diff,
                'daily_payout_rate': daily_payout_rate,
            })

        processed_records = pd.DataFrame(processed_records)
        # all time payout rate
        total_coins_in = processed_records['daily_coins_in'].sum()
        total_toys_payout = processed_records['daily_toys_payout'].sum()
        if total_coins_in == 0 or total_toys_payout == 0:
            all_time_payout_rate = 0.0
        else:
            all_time_payout_rate = total_coins_in / total_toys_payout 

        result = {
            'daily_payout_rate': processed_records['daily_payout_rate'].tolist(),
            'daily_coins_in': processed_records['daily_coins_in'].tolist(),
            'daily_toys_payout': processed_records['daily_toys_payout'].tolist(),
            'date': processed_records['date'].tolist()
        }

        return pd.DataFrame(result), all_time_payout_rate
    def plot_analyze_result(self, analyze_result):
        # Combine daily_coins_in and daily_toys_payout into a single DataFrame
        combined_df = pd.DataFrame({
            'daily_coins_in': analyze_result['daily_coins_in'],
            'daily_toys_payout': analyze_result['daily_toys_payout'],
            'date': analyze_result['date']
        })
        
        # Plot daily_coins_in and daily_toys_payout on the same plot
        print('----')
        print(analyze_result)
        print('----')
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(data=combined_df, x='date', y=['daily_coins_in', 'daily_toys_payout'])
            st.write('coins in & toys payout')
        with col2:
            st.line_chart(data=analyze_result, x='date', y='daily_payout_rate')
            st.write('payout rate')

    def save_record(self, record: Record):
        self.records_table.upsert(record.__dict__, Query().id == record.id)
        self.db.save()
