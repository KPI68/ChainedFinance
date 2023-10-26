import streamlit as st
import joblib
import numpy as np
from datetime import date
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

education_mapping = {'High School': 1, 'Diploma': 2, 'Bachelor': 3, 'Master': 4, 'PhD': 5}
loan_purpose_mapping = {'Home': 1, 'Auto': 2, 'Education': 3, 'Personal': 4}

def pin_loan_data(account_address, loan_details, file, file_hash=None):
    if file != None and file_hash == None:
        ipfs_file_hash = pin_file_to_ipfs(file.getvalue())

    if file_hash != None:
        ipfs_file_hash = file_hash

    token_json = {
        "name": account_address,
        "details": loan_details,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)
    json_ipfs_hash = pin_json_to_ipfs(json_data)
    return json_ipfs_hash, token_json

def ml_decision(loan_amount_cad, loan_term_days, details):
    gb_model = joblib.load('gb_model.pkl')
    age = details['age']
    income = details['income']
    employment_years = details['employment_years']
    education_level = details['education_level']
    education_level_num = education_mapping[education_level]
    loan_purpose = details['loan_purpose']
    loan_purpose_encoded = loan_purpose_mapping[loan_purpose]
    credit_score = details['credit_score']
    open_accounts = details['open_accounts']
    outstanding_debt = details['outstanding_debt']
    dti = details['dti']
    input_features = np.array([age, income, employment_years, education_level_num, loan_purpose_encoded,
                                credit_score, loan_amount_cad, loan_term_days, open_accounts, outstanding_debt, dti])

    # predictions using gb_model.
    gb_prediction = gb_model.predict(input_features.reshape(1, -1))
    return gb_prediction[0]==1

def loan_appraisal(account_address, loan_amount_cad, loan_term_days):

    st.title('Loan Application and Credit Worthiness Prediction')

    st.header('Customer Information')

    # Collect personal information
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
    government_id_number = st.text_input("Government ID")

    # Calculate age based on the provided DOB
    today = date.today()
    if dob:
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    else:
        age = None

    # Financial information
    income = st.number_input('Income', min_value=1)
    employment_years = st.number_input('Years of Employment', min_value=0)

    # Encode 'Education Level'
    education_level = st.selectbox('Education Level', ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'])

    # Encode 'Loan Purpose'
    loan_purpose = st.selectbox('Loan Purpose', ['Home', 'Auto', 'Education', 'Personal'])

    credit_score = st.number_input('Credit Score', min_value=300, max_value=900)
    open_accounts = st.number_input('Number of Open Accounts', min_value=0)
    outstanding_debt = st.number_input('Outstanding Debt', min_value=0)

    dti = round(outstanding_debt / income * 100, 2)

    # Register New Loan
    
    file = st.file_uploader("Upload government ID", type=["jpg", "jpeg", "png"])
    
    #  button to make the predictions
    if st.button('Submit'):
        dob_str = str(dob)
        loan_details = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob_str,
            'government_id_number': government_id_number,
            'age': age,
            'income': income,
            'outstanding_debt': outstanding_debt,
            'dti': dti,
            'employment_years': employment_years,
            'education_level': education_level,
            'loan_purpose': loan_purpose,
            'credit_score': credit_score,
            'open_accounts': open_accounts,
            'outstanding_debt': outstanding_debt
        }
        if ml_decision(loan_amount_cad, loan_term_days, loan_details):
            st.markdown("## Loan Approved")
            st.balloons()

            try:
                loan_ipfs_hash, token_json = pin_loan_data(account_address, loan_details, file)
                loan_uri = f"ipfs://{loan_ipfs_hash}"
                st.markdown(f"[Loan details Link](https://ipfs.io/ipfs/{loan_ipfs_hash})")
                return loan_uri
            except AttributeError:
                st.error("file null")
                return None
        else:
            st.error("Loan Declined")
            st.snow()
            return None

def loan_renewal(account_address, loan_amount_cad, loan_term_days, details, img_hash):

    st.title('Loan Application and Credit Worthiness Prediction')

    st.header('Customer Information')

    # Collect personal information
    st.write(f"First Name: {details['first_name']}")
    st.write(f"Last Name: {details['last_name']}")
    st.write(f"Date of Birth: {details['dob']}")
    st.write(f"Government ID: {details['government_id_number']}")

    # Calculate age based on the provided DOB
    today = date.today()
    dob = date.fromisoformat(details['dob'])
    if dob:
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    else:
        age = None

    # Financial information
    income = st.number_input('Income', min_value=1, value=details['income'])
    employment_years = st.number_input('Years of Employment', min_value=0, value=details['employment_years'])

    # Encode 'Education Level'
    education_level = st.selectbox('Education Level', 
                                   ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'],
                                   index=education_mapping[details['education_level']]-1)

    # Encode 'Loan Purpose'
    loan_purpose = st.selectbox('Loan Purpose', 
                                ['Home', 'Auto', 'Education', 'Personal'],
                                index=loan_purpose_mapping[details['loan_purpose']]-1)

    credit_score = st.number_input('Credit Score', min_value=300, max_value=900, value=details['credit_score'])
    open_accounts = st.number_input('Number of Open Accounts', min_value=0, value=details['open_accounts'])
    outstanding_debt = st.number_input('Outstanding Debt', min_value=0, value=details['outstanding_debt'])

    dti = round(outstanding_debt / income * 100, 2)

    # Register New Loan
    #  button to make the predictions
    if st.button('Submit'):
        loan_details = details
        loan_details['age'] = age
        loan_details['income'] = income
        loan_details['outstanding_debt'] = outstanding_debt
        loan_details['dti'] = dti
        loan_details['employment_years'] = employment_years
        loan_details['education_level'] = education_level
        loan_details['loan_purpose'] = loan_purpose
        loan_details['credit_score'] = credit_score
        loan_details['open_accounts'] = open_accounts
        loan_details['outstanding_debt'] = outstanding_debt
    
        if ml_decision(loan_amount_cad, loan_term_days, loan_details):
            st.markdown("## Loan Approved")
            st.balloons()

            loan_ipfs_hash, token_json = pin_loan_data(account_address, loan_details, None, img_hash)
            loan_uri = f"ipfs://{loan_ipfs_hash}"
            st.markdown(f"[Loan details Link](https://ipfs.io/ipfs/{loan_ipfs_hash})")
            return loan_uri
        else:
            st.error("Loan Declined")
            st.snow()
            return None

