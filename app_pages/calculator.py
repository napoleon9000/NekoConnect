import streamlit as st
import pandas as pd

from calculator import profit_estimation

def app():
    if 'data_input' not in st.session_state:
        st.session_state.data_input = ""

    st.title("Calculator")
    st.markdown("---")
    # profit estimation
    st.markdown("### Profit Estimation")
    # Input for data
    st.subheader("Enter transaction amounts")
    col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,8])
    with col1:
        if st.button("10"):
            if not len(st.session_state.data_input) == 0 and not st.session_state.data_input.endswith("\n"):
                st.session_state.data_input += "\n"
            st.session_state.data_input += "10\n"
    with col2:
        if st.button("20"):
            if not len(st.session_state.data_input) == 0 and not st.session_state.data_input.endswith("\n"):
                st.session_state.data_input += "\n"
            st.session_state.data_input += "20\n"
    with col3:
        if st.button("50"):
            if not len(st.session_state.data_input) == 0 and not st.session_state.data_input.endswith("\n"):
                st.session_state.data_input += "\n"
            st.session_state.data_input += "50\n"
    with col4:
        if st.button("100"):
            if not len(st.session_state.data_input) == 0 and not st.session_state.data_input.endswith("\n"):
                st.session_state.data_input += "\n"
            st.session_state.data_input += "100\n"
    with col5:
        if st.button("Clear"):
            st.session_state.data_input = ""

    data_input = st.text_area("Enter amounts (one per line):", value=st.session_state.data_input, height=150)
    st.session_state.data_input = data_input

    # Convert input to list of integers
    data = [int(x.strip()) for x in data_input.split('\n') if x.strip().isdigit()]

    # Input for parameters
    st.subheader("Parameters")
    toys_payout_rate = st.number_input("Toys payout rate:", value=1/7.0, format="%.4f", step=0.0001)
    avg_toys_cost = st.number_input("Average toys cost:", value=2.5, step=0.1)
    fixed_cost = st.number_input("Fixed cost:", value=400, step=10)

    if st.button("Calculate Profit"):
        if data:
            profit, total_income, total_tokens, toys_payout = profit_estimation(
                data, toys_payout_rate, avg_toys_cost, fixed_cost
            )
            
            st.subheader("Results")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Income", f"${total_income:.2f}")
                st.metric("Total Tokens", total_tokens)
            with col2:
                st.metric("Toys Payout", f"{toys_payout:.2f}")
                st.metric("Profit", f"${profit:.2f}")
            
            # Display input data as a table
            st.subheader("Input Data")
            df = pd.DataFrame({"Amount": data})
            st.dataframe(df.T)
        else:
            st.error("Please enter valid transaction amounts.")

if __name__ == "__main__":
    app()