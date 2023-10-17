import streamlit as st
import json
import requests
import os
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv

@st.cache_resource()

def get_CADR():
    # get current ETH rate from coinbase
    api_uri = "https://api.coinbase.com/v2/prices/ETH-CAD/buy?format=json"
    resp = requests.get(api_uri)
    rate_json = json.loads(resp.content.decode('utf8').replace("'", '"'))
    rate_eth = float(rate_json['data']['amount'])
    return rate_eth
    
def input_ETH():
    eth = st.number_input("Number of ETH")
    st.write(f"CAD Equivalent {round(eth*get_CADR(),2)}")
    return eth

def deposit():    
    num_eth = input_ETH()
    int_rate = st.slider("Propose Annual Interest Rate in unit of 0.001", max_value=300)
    st.write(f"{int_rate*0.1}%")
    return num_eth

def submit_deposit(eth):
    st.markdown("## deposit to contract, update Interest contract")
    tx_hash = acc_contract.functions.deposit().transact(
        {   "from": msg_sender, 
            "value": w3.toWei(eth,'ether'), 
            "gas":100000,
            'gasPrice': w3.toWei('25', 'gwei') })
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write(receipt)

def withdraw():
    return input_ETH()

def submit_withdraw(num_eth):
    st.markdown("## contract.transfer")
    print(num_eth)
    tx_hash = acc_contract.functions.withdraw(w3.toWei(num_eth,'ether')).transact(
        {   "from": msg_sender,
            "gas":100000,
            'gasPrice': w3.toWei('25', 'gwei') 
        })
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write(receipt)

def check_balance():
    bal_wei = acc_contract.functions.current_balance().call(
        {   "from": msg_sender, 
            "gas": 100000
        }
    )
    st.write(f"{w3.fromWei(bal_wei,"ether")} ETH")

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
            "Check Balance": { "input": check_balance, "submit": None },
            "Apply Loan": { "input": apply_loan, "submit": submit_apply_loan },
            "Repay Loan": { "input": repay_loan, "submit": submit_repay_loan },
            "Renew Loan": { "input": renew_loan, "submit": submit_renew_loan },
            "Request Interest": { "input": request_interest, "submit": submit_request_interest },
            "Collector": { "input": collector, "submit": submit_collector }
        }

st.image("Images/fish.png")
st.markdown("# Fin Fishing")

load_dotenv()

# connect to Ganache
w3 =  Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
    
with open(Path('./contracts/compiled/acc_abi.json')) as f:
    acc_abi = json.load(f)

acc_contract_address = os.getenv("ACC_CONTRACT_ADDRESS")
acc_contract = w3.eth.contract(address=acc_contract_address, abi=acc_abi)    
st.markdown(f"## Current System Total {w3.fromWei(w3.eth.get_balance(acc_contract_address),'ether')} 
            ETH")

msg_sender = st.text_input("Ethereum Account")

func_selected = st.selectbox("Select a function:", funcs.keys() )
eth_num = funcs[func_selected]["input"]()
if st.button("Submit"):
    funcs[func_selected]["submit"](eth_num)
