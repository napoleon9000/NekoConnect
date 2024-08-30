import streamlit as st
from tinydb import TinyDB, Query
from datetime import datetime
from backend import create_user, edit_user, delete_user, find_user, record_redemption, display_user_info
import logging
import pandas as pd
from app_pages.edit_user import app as edit_user_page
from app_pages.add_new_user import app as add_new_user_page


logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="NekoConnect",
    layout="wide",
    )

# Initialize the database
db = TinyDB('nekoconnect_db.json')
users_table = db.table('users')

# init session state
if 'selected_user' not in st.session_state:
    st.session_state['selected_user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

def switch_page(page):
    st.session_state['page'] = page

st.sidebar.button("Home", on_click=switch_page, args=('home',), use_container_width=True)
st.sidebar.button("Add New User", on_click=switch_page, args=('add_new_user',), use_container_width=True)
st.sidebar.button("Edit User", on_click=switch_page, args=('edit_user',), use_container_width=True)

def home_page():
    # Page functionality
        st.title("NekoConnect")
        st.markdown("### All Users")

        # find all users
        all_info = display_user_info()
        if all_info is None:
            st.info("No users found. Please add a new user.")
            return
        
        # search bar
        col1, col2 = st.columns([3, 1])
        with col1:
            search_phone = st.text_input("Enter phone number to search user")
        with col2:
            if st.button("Clear", use_container_width=True):
                search_phone = ""
        if search_phone:
            all_info = all_info[all_info['phone_number'] == search_phone]
        
        st.markdown("---")
        

        def on_edit_click(index):
            st.session_state['selected_user'] = all_info.iloc[index]
            st.session_state['page'] = 'edit_user'


        def on_delete_click(index):
            phone_number = all_info.iloc[index]['phone_number']
            delete_user(phone_number)

        for index, row in all_info.iterrows():
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                row = pd.DataFrame(row).T
                st.dataframe(row, use_container_width=True)
            with col2:
                st.button("Edit", key=f"edit_{index}", use_container_width=True, on_click=on_edit_click, args=(index,))
            with col3:
                st.button("Delete", key=f"delete_{index}", use_container_width=True, on_click=on_delete_click, args=(index,))


if st.session_state['page'] == 'home':
    home_page()

elif st.session_state['page'] == 'edit_user':
    edit_user_page()

elif st.session_state['page'] == 'add_new_user':
    add_new_user_page()