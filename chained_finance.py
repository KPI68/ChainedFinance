import streamlit as st
import json
import requests

@st.cache_resource()

def get_CADR():
    # get current ETH rate from coinbase
    api_uri = "https://api.coinbase.com/v2/prices/ETH-CAD/buy?format=json"
    resp = requests.get(api_uri)
    rate_json = json.loads(resp.content.decode('utf8').replace("'", '"'))
    rate_eth = float(rate_json['data']['amount'])
    return rate_eth
    
def input_ETH():
    num_eth = st.number_input("Number of ETH")
    st.write(f"CAD Equivalent {round(num_eth*get_CADR(),2)}")
    return num_eth

def deposit():    
    num_eth = input_ETH()
    int_rate = st.slider("Propose Annual Interest Rate in unit of 0.001", max_value=300)
    st.write(f"{int_rate*0.1}%")

def submit_deposit():
    st.markdown("## deposit to contract, update Interest contract")

def withdraw():
    num_eth = input_ETH()

def submit_withdraw():
    st.markdown("## contract.transfer")

def apply_loan():
    st.markdown("## Input info ERC721Full")
    purpose = st.selectbox("Purpose of loan", ["Grocery", "Bet", "Drug", "Rent"])
    allowance = input_ETH()
    tenor = st.slider("Select tenor in days", min_value=1, max_value=365)

def submit_apply_loan():
    st.markdown("## Run AI grant Y/N")
    st.markdown("## Withdraw under allowance + Reg Loan ERC721Full")

def repay_loan():
    st.markdown("## Repay loan")
    num_eth = input_ETH()

def submit_repay_loan():
    st.markdown("## deposit + update Loan ERC721Full + update Interest Contract")

def renew_loan():
    st.markdown("## Call up from ERC721Full")
    allowance = input_ETH()
    tenor = st.slider("Select tenor in days", min_value=1, max_value=365)

def submit_renew_loan():
    st.markdown("## New allowance is 30 starting today")
    st.markdown("## Withdraw allowance less loan less interest + Reg Loan ERC721Full")

def request_interest():
    num_eth = input_ETH()

def submit_request_interest():
    st.markdown("## Withdraw from Interest Contract")

def collector():
    st.write("### Get and show current commission rate from the Interest contract is 0.1")
    st.markdown("## list delinquent loans to select see/pay")

def submit_collector():
    st.markdown("## payback a loan less commision")

funcs = {   "Deposit": { "input": deposit, "submit": submit_deposit },
            "Withdraw": { "input": withdraw, "submit": submit_withdraw },
            "Apply Loan": { "input": apply_loan, "submit": submit_apply_loan },
            "Repay Loan": { "input": repay_loan, "submit": submit_repay_loan },
            "Renew Loan": { "input": renew_loan, "submit": submit_renew_loan },
            "Request Interest": { "input": request_interest, "submit": submit_request_interest },
            "Collector": { "input": collector, "submit": submit_collector }
        }

st.image("Images/fish.png")
st.markdown("# Fin Fishing")

msg_sender = st.text_input("Ethereum Account")

func_selected = st.selectbox("Select a function:", funcs.keys() )
funcs[func_selected]["input"]()
if st.button("Submit"):
    funcs[func_selected]["submit"]()
