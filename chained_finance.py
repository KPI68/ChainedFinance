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

def register_loan(loan_uri, tenor):
    tx_hash = loan_contract.functions.registerLoan(str(datetime.date.today()), tenor,
        loan_uri).transact({'from': msg_sender, 'gas': 1000000})
    loan_id = loan_contract.functions.totalSupply().call() - 1
    
    tx_hash = acc_contract.functions.set_loan_id(loan_id).transact(
        {   "from": msg_sender}
    )

    st.markdown(f"## Loan amount: {get_loan_amount()} ETH")

def cash_loan(loan_amount_eth):
    try:
        tx_hash = acc_contract.functions.cash_loan(w3.toWei(loan_amount_eth,'ether')).transact(
            {   "from": msg_sender,
                "gas":100000,
                'gasPrice': w3.toWei('25', 'gwei') 
            })
    except ValueError as e:
        st.error(ast.literal_eval(str(e))['message'], icon="🚨")
        return False
    return True
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)

def update_loan(loan_id, tenor, loan_uri):
    tx_hash = loan_contract.functions.updateLoan(loan_id, str(datetime.date.today()), tenor,
        loan_uri).transact({'from': msg_sender, 'gas': 1000000})
    
    tx_hash = acc_contract.functions.set_loan_id(loan_id).transact(
        {   "from": msg_sender}
    )

    st.markdown(f"## Loan amount: {get_loan_amount()} ETH")

def expose_delinquents():
    # Fetch total number of properties/tokens
    total_loans = loan_contract.functions.totalSupply().call()
    loan_ids = list(range(total_loans))

    loan_id = st.selectbox("Choose a Loan ID", loan_ids)
    get_loan_details(loan_id, for_delinquent=True)

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

def get_loan_details(loan_id, for_delinquent=False):
    start_date_str, tenor, loan_uri = loan_contract.functions.getLoanDetails(loan_id).call()
    if for_delinquent:
        start_date = datetime.date.fromisoformat(start_date_str)
        passed_days = (datetime.date.today() - start_date).days
        if passed_days < tenor:
            st.error("Loan not pastdue", icon="🤖")
            return
    return start_date_str, tenor, loan_uri

def display_loan_details(loan_uri): 
    ipfs_hash = loan_uri[7:]
    st.sidebar.markdown(f"[IPFS Gateway Link for Loan detail](https://ipfs.io/ipfs/{ipfs_hash})")
    response = urlopen(f"https://ipfs.io/ipfs/{ipfs_hash}") 
    data_json = json.loads(response.read()) 
    loan_details = dict(data_json)
    if loan_details["name"] != msg_sender:
        return None
    st.sidebar.write(data_json)
    st.sidebar.image(f'https://ipfs.io/ipfs/{loan_details["image"]}')
    return loan_details

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
        st.markdown(f"## {float(w3.fromWei(w3.eth.get_balance(acc_contract_address),'ether'))}")
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
    st.sidebar.markdown(f"## Your current balance is {bal_eth} ETH")
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
    loan_amount = get_loan_amount()
    if loan_amount != 0:
        st.error("Account already has loan. Go to Renew function.")
        return
    
    allowance = input_ETH()
    allowance_in_cad = round(allowance*get_CADR(),2)
    tenor = st.slider("Select tenor in days", min_value=1, max_value=366)
    try:
        loan_uri = loan_appraisal(msg_sender, allowance_in_cad, tenor)
    except TypeError:
        loan_uri = None

    if loan_uri != None:
        if cash_loan(allowance):
            register_loan(loan_uri, tenor)
        display_loan_details(loan_uri)

def repay_loan():
    loan_amount = get_loan_amount()
    if loan_amount == 0:
        st.error("Account has no loan")
        return
    
    loan_id = acc_contract.functions.get_loan_id().call( {"from": msg_sender} )
    start_date_str, tenor, loan_uri = get_loan_details(loan_id)
    if  start_date_str == None:
        st.error("Account has no loan")
        return
    
    start_date = datetime.date.fromisoformat(start_date_str)
    passed_days = (datetime.date.today() - start_date).days
    interest_rate = acc_contract.functions.get_rate().call()

    eth = input_ETH()
    passed_days = 10
    total_interest = eth * interest_rate * passed_days / 365000
    st.sidebar.markdown(f"## Repay - Loan Amount: {loan_amount} ETH")
    st.sidebar.markdown(f"## borrowed for: {passed_days} days")
    st.sidebar.markdown(f"## at annual rate: {interest_rate / 10}%")
    st.sidebar.markdown(f"## Total Interest to pay: {total_interest} ETH")

    display_loan_details(loan_uri)

    if st.button('Submit'): 
        try:
            tx_hash = acc_contract.functions.repay_loan().transact(
                {   "from": msg_sender, 
                    "value": w3.toWei(eth,'ether'), 
                    "gas":100000 })
        except ValueError as e:
            st.error(ast.literal_eval(str(e))['message'])
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
    start_date_str, tenor, loan_uri = get_loan_details(loan_id)
    if start_date_str == None:
        st.error("Account has no loan")
        return

    old_amount = get_loan_amount()
    st.sidebar.markdown(f"## Renew - Loan Amount: {old_amount} ETH")
    st.sidebar.markdown(f"## Tenor: {tenor} days")
    st.sidebar.markdown(f"## Start Date: {start_date_str}")
    loan_details = display_loan_details(loan_uri)

    allowance = int(input_ETH())
    allowance_in_cad = round(allowance*get_CADR(),2)
    tenor = st.slider("Select tenor in days", min_value=1, max_value=366)
    loan_uri = loan_renewal(msg_sender, allowance_in_cad, tenor, 
                            loan_details['details'], loan_details["image"])
    if loan_uri == None:
        return
    
    tx_hash = loan_contract.functions.updateLoan(loan_id, str(datetime.date.today()), tenor, loan_uri).transact({'from': msg_sender, 'gas': 1000000})
    
    start_date = datetime.date.fromisoformat(start_date_str)
    passed_days = (datetime.date.today() - start_date).days
    interest_rate = acc_contract.functions.get_rate().call()

    passed_days = 10
    if allowance >= old_amount:
        total_interest = old_amount * interest_rate * passed_days / 365000
    else:
        total_interest = (old_amount - allowance) * interest_rate * passed_days / 365000

    if allowance > old_amount and not cash_loan(allowance-old_amount):
        return
    
    st.markdown(f"## borrowed for: {passed_days} days")
    st.markdown(f"## at annual rate: {interest_rate / 10}%")
    st.markdown(f"## Total Interest to pay: {total_interest} ETH")
    display_loan_details(loan_uri)

    update_loan(loan_id, tenor, loan_uri)
    if total_interest > 0:
        tx_hash = acc_contract.functions.repay_interest().transact(
        {   "from": msg_sender, 
            "value": w3.toWei(total_interest,'ether'), 
            "gas":100000 
        })
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt)
        
    
def request_interest():
    earned_interest = acc_contract.functions.current_interest().call()
    st.markdown(f"## Earned Interest: {earned_interest}")

    if earned_interest == 0:
        return
    
    if st.button('Submit'):
        try:
            tx_hash = acc_contract.functions.cash_interest(w3.toWei(earned_interest,'ether')).transact(
                { "from": msg_sender,
                "gas":100000})
        except ValueError as e:
            st.error(ast.literal_eval(str(e))['message'])
            return
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write(receipt) 

def collector():
    expose_delinquents()

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
