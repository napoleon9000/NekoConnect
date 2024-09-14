import streamlit as st
from backend import Manager

def app():
    st.subheader("Add New User")
    mgr = Manager()
    phone_number = st.text_input("Phone Number")
    name = st.text_input("Name (Optional)")
    if st.button("Save"):
        mgr.create_user(phone_number, name)
        st.success(f"User {phone_number} has been successfully created!")

if __name__ == "__main__":
    app()
    st.write(st.session_state)