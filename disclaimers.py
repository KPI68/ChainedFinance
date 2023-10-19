import streamlit as st

def deposit_rules():
    st.markdown("#### Deposit from your Ethereum account to our system")
    st.markdown("#### The principal of the deposit can be withdrawn at anytime in full unless system is out of cash")
    st.markdown("#### Require an interest rate which will participate in the calculation of our Rate weighted by this amount")
    st.markdown("#### Request Interest function would use our Rate as at the requesting time")
    st.markdown("#### Interest can be withdrawn in the lesser of the two amounts:")
    st.markdown("* Your deposited aggregated balance times our rate")
    st.markdown("* The system total available interest paid by debtors")

#deposit_rules()