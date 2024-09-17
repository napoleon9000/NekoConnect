import streamlit as st
import pandas as pd
from dataclasses import dataclass
import logging

from toy_record import Manager, Machine
from io import BytesIO

logger = logging.getLogger(__name__)

def app():
    st.title("Machines")
    st.markdown("---")

    # show all machines and images
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    machines = manager.get_all_machines()
    num_columns = 4
    columns = st.columns(num_columns)

    for idx, machine in enumerate(machines):
        name = machine['name']
        location = machine['location']
        status = machine['status']
        notes = machine['notes']
        image = manager.get_image_by_machine_id(machine['id'])

        # Determine which column to use
        col = columns[idx % num_columns]

        with col:
            st.image(image, width=200)
            if name is not None and name != "":
                st.markdown(f"**Name:** {name}")
            else:
                st.markdown(f"**id:** {machine['id']}")
            if location is not None and location != "":
                st.markdown(f"**Location:** {location}")
            if status is not None and status != "":
                st.markdown(f"**Status:** {status}")
            if notes is not None and notes != "":
                st.markdown(f"**Notes:** {notes}")

    # create machine (in an expander)
    with st.expander("Add New Machine"):
        st.write("Add New Machine")
        name = st.text_input("Name")
        location = st.text_input("Location")
        status = st.text_input("Status")
        notes = st.text_input("Notes")
        image = st.file_uploader("Image", type=["jpg", "png"])
        logger.info(f"Image: {image}")
        if st.button("Save"):
            new_machine = Machine(name, location, status, notes)
            logger.info(f"New machine: {new_machine}")
            img_bytesio = BytesIO(image.getvalue())
            manager.create_machine(new_machine, img_bytesio)
            st.success("Machine created successfully")

    
if __name__ == "__main__":
    app()