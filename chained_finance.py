import streamlit as st
import json
import ast
import requests
import os
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
from disclaimers import deposit_rules
from applyfunction import loan_appraisal, loan_renewal
from urllib.request import urlopen 
import datetime

#@st.cache_resource()

def register_loan(loan_amount_eth, loan_uri, tenor):
    try:
        tx_hash = acc_contract.functions.cash_loan(w3.toWei(loan_amount_eth,'ether')).transact(
            {   "from": msg_sender,
                "gas":100000,
                'gasPrice': w3.toWei('25', 'gwei') 
            })
    except ValueError as e:
        st.write(ast.literal_eval(str(e))['message'])
        return
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    tx_hash = loan_contract.functions.registerLoan(str(datetime.date.today()), tenor,
        loan_uri).transact({'from': msg_sender, 'gas': 1000000})
    loan_id = loan_contract.functions.totalSupply().call() - 1
    
    tx_hash = acc_contract.functions.set_loan_id(loan_id).transact(
        {   "from": msg_sender}
    )

    st.write(f"Loan amount: {get_loan_amount()} ETH")

def expose_delinquents():
    # Fetch total number of properties/tokens
    total_loans = loan_contract.functions.totalSupply().call()
    loan_ids = list(range(total_loans))

    st.markdown("## Display loan id:")
    loan_id = st.selectbox("Choose a Loan ID", loan_ids)
    get_loan_details(loan_id)

def get_CADR():
    # get current ETH rate from coinbase
    api_uri = "https://api.coinbase.com/v2/prices/ETH-CAD/buy?format=json"
    resp = requests.get(api_uri)
    rate_json = json.loads(resp.content.decode('utf8').replace("'", '"'))
    rate_eth = float(rate_json['data']['amount'])
    return rate_eth
    
def input_ETH(max_value=None):
    eth = st.number_input("Number of ETH", max_value=max_value)
    st.write(f"CAD Equivalent {round(eth*get_CADR(),2)}")
    return eth

def do_nothing():
    pass

def get_loan_amount():
    loan_wei = acc_contract.functions.current_loan().call(
        {   "from": msg_sender, 
            "gas": 100000
        }
    )
    return w3.fromWei(loan_wei,'ether')

def get_loan_tenor(loan_id):
    return loan_contract.functions.getLoanTenor(loan_id).call()

def get_loan_start_date(loan_id):
    start_date_str = loan_contract.functions.getStartDate(loan_id).call()
    return datetime.date.fromisoformat(start_date_str)

def get_loan_details(loan_id):
    loan_uri = loan_contract.functions.getLoanDetails(loan_id).call()
    ipfs_hash = loan_uri[7:]
    st.markdown(f"[IPFS Gateway Link for Loan detail](https://ipfs.io/ipfs/{ipfs_hash})")
    response = urlopen(f"https://ipfs.io/ipfs/{ipfs_hash}") 
    data_json = json.loads(response.read()) 
    loan_details = dict(data_json)
    if loan_details["name"] != msg_sender:
        return None
    st.write(data_json)
    st.image(f'https://ipfs.io/ipfs/{loan_details["image"]}')
    return dict(data_json)

def deposit():    
    deposit_rules()
    num_eth = input_ETH()
    int_rate = st.slider("Propose Annual Interest Rate in unit of 0.001", max_value=300)
    st.write(f"{int_rate*0.1}%")

    if st.button('Submit'):
        tx_hash = acc_contract.functions.deposit().transact(
            {   "from": msg_sender, 
                "value": w3.toWei(num_eth,'ether'), 
                "gas":100000,
                'gasPrice': w3.toWei('25', 'gwei') })
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt)
        st.write(int(w3.fromWei(w3.eth.get_balance(acc_contract_address),'ether')))
        acc_contract.functions.set_rate(int_rate).transact(
            {   "from": msg_sender
            }
        )

def withdraw():
    bal_wei = acc_contract.functions.current_cash().call(
        {   "from": msg_sender
        }
    )
    bal_eth = w3.fromWei(bal_wei,'ether')
    st.write(f"Your current balance is {bal_eth} ETH")
    num_eth = input_ETH(float(bal_eth))

    if st.button('Submit'):
        if num_eth == 0:
            return
        
        try:
            tx_hash = acc_contract.functions.withdraw(w3.toWei(num_eth,'ether')).transact(
                {  "from": msg_sender,
                    "gas":100000
                })
                #'gasPrice': w3.toWei('25', 'gwei') 
        except ValueError as e:
            st.write(ast.literal_eval(str(e))['message'])
            return
        
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt)

def apply_loan():
    allowance = input_ETH()
    allowance_in_cad = round(allowance*get_CADR(),2)
    tenor = st.slider("Select tenor in days", min_value=1, max_value=366)
    try:
        loan_details, loan_uri = loan_appraisal(msg_sender, allowance_in_cad, tenor)
    except TypeError:
        loan_details = None

    if loan_details != None:
        register_loan(allowance, loan_uri)

def repay_loan():
    loan_amount = get_loan_amount()
    if loan_amount == 0:
        st.write("Account has no loan")
        return
    
    loan_id = acc_contract.functions.get_loan_id().call( {"from": msg_sender} )
    loan_details = get_loan_details(loan_id)
    if loan_details == None:
        st.write("Account has no loan")
        return
    
    start_date = get_loan_start_date(loan_id)
    passed_days = (datetime.date.today() - start_date).days
    interest_rate = acc_contract.functions.get_rate().call()

    eth = input_ETH()
    passed_days = 1
    total_interest = eth * interest_rate * passed_days / 365000
    st.markdown(f"## Repay - Loan Amount: {loan_amount} ETH")
    st.markdown(f"borrowed for: {passed_days} days")
    st.markdown(f"at annual rate: {interest_rate / 10}%")
    st.markdown(f"Total Interest to pay: {total_interest} ETH")

    if st.button('Submit'): 
        try:
            tx_hash = acc_contract.functions.repay_loan().transact(
                {   "from": msg_sender, 
                    "value": w3.toWei(eth,'ether'), 
                    "gas":100000 })
        except ValueError as e:
            st.write(ast.literal_eval(str(e))['message'])
            return
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt)

        tx_hash = acc_contract.functions.repay_interest().transact(
                {   "from": msg_sender, 
                    "value": w3.toWei(total_interest,'ether'), 
                    "gas":100000 
                })
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt)

def renew_loan():
    loan_id = acc_contract.functions.get_loan_id().call( {"from": msg_sender} )
    loan_details = get_loan_details(loan_id)
    if loan_details == None:
        st.write("Account has no loan")
        return

    st.markdown(f"## Renew - Loan Amount: {get_loan_amount()} ETH")
    allowance = input_ETH()
    allowance_in_cad = round(allowance*get_CADR(),2)
    loan_details["detail"]["allowance_in_cad"] = allowance_in_cad
    tenor = st.slider("Select tenor in days", min_value=1, max_value=366)
    if not loan_renewal(loan_details, tenor):
        return
    
    tx_hash = loan_contract.functions.setStartDate(str(datetime.date.today())).transact({'from': msg_sender, 'gas': 1000000})
    tx_hash = loan_contract.functions.setTenor(tenor).transact({'from': msg_sender, 'gas': 1000000})

def request_interest():
    st.markdown(f"## Earned Interest: {acc_contract.functions.current_interest().call()}")
    eth = input_ETH()
    if st.button('Submit'):
        try:
            tx_hash = acc_contract.functions.cash_interest(w3.toWei(eth,'ether')).transact(
                { "from": msg_sender,
                "gas":100000})
        except ValueError as e:
            st.write(ast.literal_eval(str(e))['message'])
            return
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt) 

def collector():
    st.write("### Get and show current commission rate from the Interest contract is 0.1")
    st.markdown("## list delinquent loans to select see/pay")

funcs = {   "Deposit": deposit,
            "Withdraw": withdraw,
            "Apply Loan": apply_loan,
            "Repay Loan": repay_loan,
            "Renew Loan": renew_loan,
            "Request Interest": request_interest,
            "Collector": collector
        }

cash_last, loan_last, interest_last = 0, 0, 0
loan_details = None

st.image("Images/fish.png", caption="Fin Fishing")
#st.markdown("# Fin Fishing")

load_dotenv()

# connect to Ganache
w3 =  Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
    
with open(Path('./contracts/compiled/acc_abi.json')) as f:
    acc_abi = json.load(f)
acc_contract_address = os.getenv("ACC_CONTRACT_ADDRESS")
acc_contract = w3.eth.contract(address=acc_contract_address, abi=acc_abi)

with open(Path('./contracts/compiled/loan_abi.json')) as f:
    loan_abi = json.load(f)
loan_contract_address = os.getenv("LOAN_CONTRACT_ADDRESS")
loan_contract = w3.eth.contract(address=loan_contract_address, abi=loan_abi)

cash = float(w3.fromWei(w3.eth.get_balance(acc_contract_address),'ether'))
loan = float(w3.fromWei(acc_contract.functions.get_total_loan().call(),'ether'))
interest = float(w3.fromWei(acc_contract.functions.get_total_interest().call(),'ether'))

st.markdown(f"#### Current System Interest Rate: {acc_contract.functions.get_rate().call()} units of 0.001")
kpi1, kpi2, kpi3 = st.columns(3)

# fill in those three columns with respective metrics or KPIs
kpi1.metric(
    label="Total Cash",
    value=cash,
    delta=cash - cash_last
)
        
kpi2.metric(
    label="Total Loan 💍",
    value=loan,
    delta=loan - loan_last
)
        
kpi3.metric(
    label="Total Interest 💍",
    value=interest,
    delta=interest - interest_last
)

cash_last = cash
loan_last = loan
interest_last = interest

#msg_sender = st.text_input("Ethereum Account")
msg_sender = st.selectbox("Account Address:", w3.eth.accounts)

func_selected = st.selectbox("Select a function:", funcs.keys() )
funcs[func_selected]()
