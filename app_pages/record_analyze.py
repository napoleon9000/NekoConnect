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
    all_results = []
    
    st.markdown("#### Individual Machine Analysis")
    for machine in machines:
        cols = st.columns([1, 8])
        machine_id = machine.id
        analyze_result, all_time_payout_rate = manager.calculate_machine_payout_rate(machine_id)
        all_results.append(analyze_result)
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

    st.markdown("#### Overall Analysis")
    all_dates = all_results[0]['date']
    data_by_date = {k: {
        'daily_payout_rate': [],    
        'daily_coins_in': [],
        'daily_toys_payout': []
    } for k in all_dates}

    for result in all_results:
        for date in all_dates:
            print(f'results_daily_payout_rate: {result["daily_payout_rate"]}')
            daily_payout_rate = result['daily_payout_rate'].loc[result['date'] == date].values[0]
            daily_coins_in = result['daily_coins_in'].loc[result['date'] == date].values[0]
            daily_toys_payout = result['daily_toys_payout'].loc[result['date'] == date].values[0]
            
            data_by_date[date]['daily_payout_rate'].append(daily_payout_rate)
            data_by_date[date]['daily_coins_in'].append(daily_coins_in)
            data_by_date[date]['daily_toys_payout'].append(daily_toys_payout)
    
    # sum each date
    for date in all_dates:
        data_by_date[date]['daily_payout_rate'] = sum(data_by_date[date]['daily_payout_rate']) / len(data_by_date[date]['daily_payout_rate'])
        data_by_date[date]['daily_coins_in'] = sum(data_by_date[date]['daily_coins_in'])
        data_by_date[date]['daily_toys_payout'] = sum(data_by_date[date]['daily_toys_payout'])

    # plot
    df_all = pd.DataFrame(data_by_date).T.reset_index()
    df1 = df_all[['daily_coins_in', 'daily_toys_payout']]
    df1['date'] = all_dates.values
    df2 = df_all[['daily_payout_rate']]
    df2['date'] = all_dates.values

    cols = st.columns(2)
    with cols[0]:
        st.line_chart(df1, y=['daily_coins_in', 'daily_toys_payout'], x='date')
        with st.expander("Detail Records", expanded=False):
            st.dataframe(df1)
    with cols[1]:
        st.line_chart(df2, y='daily_payout_rate', x='date')
        with st.expander("Detail Records", expanded=False):
            st.dataframe(df2)

if __name__ == "__main__":
    app()