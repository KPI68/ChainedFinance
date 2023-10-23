import streamlit as st
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

# Load environment variables
#load_dotenv()

# Connect to Web3 provider
#w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Load the contract
#@st.cache_resource()

# Helper functions for pinning
def pin_loan_data(account_address, loan_details, file):
    ipfs_file_hash = pin_file_to_ipfs(file.getvalue())
    token_json = {
        "account": account_address,
        "details": loan_details,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)
    json_ipfs_hash = pin_json_to_ipfs(json_data)
    return json_ipfs_hash, token_json

def register_loan(contract, account_address, loan_details):
    # Register New Loan
    file = st.file_uploader("Upload government ID", type=["jpg", "jpeg", "png"])

    if st.button("Register"):
        loan_ipfs_hash, token_json = pin_loan_data(account_address, loan_details, file)
        loan_uri = f"ipfs://{loan_ipfs_hash}"

        tx_hash = contract.functions.registerLoan(
            account_address,                # ownerAddress
            loan_details['loan_amount'],    # amount in ETH
            loan_details['tenor'],          
            loan_details['start_date'],
            loan_uri).transact({'from': account_address, 'gas': 1000000})
    
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        st.markdown(f"[Loan details Link](https://ipfs.io/ipfs/{loan_ipfs_hash})")
        return True
    
    return False
    st.markdown("---")

def expose_delinquents(contract):
    # Fetch total number of properties/tokens
    total_loans = contract.functions.totalSupply().call()
    loan_ids = list(range(total_loans))

    st.markdown("## Display loan id:")
    loan_id = st.selectbox("Choose a Loan ID", loan_ids)

    loan_json = contract.functions.getLoanDetails(loan_id).call()

    if isinstance(loan_json, str):
        loan_data = convert_data_to_json(loan_json)
    else:
        st.write("Error: Loan details are not valid strings.")

