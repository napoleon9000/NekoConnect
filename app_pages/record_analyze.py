import streamlit as st
import pandas as pd
from dataclasses import dataclass

from toy_record import Manager, Record



def app():
    st.title("Toys Record Analyzer")
    st.markdown("---")

    # show all machines and images
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    machines = manager.get_all_machines_obj()

    for machine in machines:
        cols = st.columns([1, 8])
        machine_id = machine.id
        analyze_result, all_time_payout_rate = manager.calculate_machine_payout_rate(machine_id)
        with cols[0]:
            machine_image = manager.get_image_by_machine_id(machine_id)
            name = machine.name
            location = machine.location
            st.image(machine_image, width=150)
            if name is not None and name != "":
                st.markdown(f"**Name:** {name}")
            else:
                st.markdown(f"**id:** {machine_id}")
            if location is not None and location != "":
                st.markdown(f"**Location:** {location}")
            st.markdown(f"**All Time Payout Rate:** {all_time_payout_rate:.2f}")
            st.markdown(f"**Last Payout Rate:** {analyze_result['daily_payout_rate'].tolist()[-1]:.2f}") 
            st.markdown(f"**Machine Params:** {machine.get_params()}")

        with cols[1]:
            manager.plot_analyze_result(analyze_result)
        
        with st.expander("Detail Records", expanded=False):
            df = manager.get_records_by_machine_id(machine_id)
            st.dataframe(df)
        
        st.markdown("---")

if __name__ == "__main__":
    app()