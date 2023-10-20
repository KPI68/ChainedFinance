import streamlit as st
import joblib
import numpy as np
from datetime import date

def apply_loan():
 
    gb_model = joblib.load('gb_model.pkl')

    st.title('Loan Application and Credit Worthiness Prediction')

    st.header('Customer Information')

    # Collect personal information
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
    government_id_number = st.text_input("Government ID")

    # Calculate age based on the provided DOB
    if dob:
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    else:
        age = None

    # Financial information
    income = st.number_input('Income', min_value=1)
    employment_years = st.number_input('Years of Employment', min_value=0)

    # Encode 'Education Level'
    education_level = st.selectbox('Education Level', ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'])
    education_mapping = {'High School': 1, 'Diploma': 2, 'Bachelor': 3, 'Master': 4, 'PhD': 5}
    education_level_num = education_mapping[education_level]

    # Encode 'Loan Purpose'
    loan_purpose = st.selectbox('Loan Purpose', ['Home', 'Auto', 'Education', 'Personal'])
    loan_purpose_mapping = {'Home': 1, 'Auto': 2, 'Education': 3, 'Personal': 4}
    loan_purpose_encoded = loan_purpose_mapping[loan_purpose]

    credit_score = st.number_input('Credit Score', min_value=300, max_value=900)
    open_accounts = st.number_input('Number of Open Accounts', min_value=0)
    outstanding_debt = st.number_input('Outstanding Debt', min_value=0)
    loan_amount_eth = st.number_input('Loan Amount in ETH', min_value=0)
    loan_term_days = st.number_input('Loan Term in Days', min_value=1, max_value=366)

    # convert ETH input into CAD value before passing to ML model.
    eth_to_cad_rate = get_CADR()
    loan_amount_cad = loan_amount_eth * eth_to_cad_rate

    dti = round(outstanding_debt / income * 100, 2)

    #  button to make the predictions
    if st.button('Apply for Loan'):
        input_features = np.array([age, income, employment_years, education_level_num, loan_purpose_encoded,
                                   credit_score, loan_amount_cad, loan_term_days, open_accounts, outstanding_debt, dti])

        # predictions using gb_model.
        gb_prediction = gb_model.predict(input_features.reshape(1, -1))

        if gb_prediction[0] == 1:
            st.write("Loan Approved")
        else:
            st.write("Loan Declined")


