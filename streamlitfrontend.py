import streamlit as st
import joblib
import numpy as np
from datetime import date

# Load trained machine learning models

#rf_model = joblib.load('random_forest_model.pkl')
gb_model = joblib.load('gb_model.pkl')

# Streamlit  title
st.title('Credit Worthiness Prediction')

#  input fields for customer information
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
education_level = st.selectbox('Education Level', ['High School','Diploma', 'Bachelor', 'Master', 'PhD'])
education_mapping = {'High School': 1, 'Diploma':2, 'Bachelor': 3,  'Master': 4, 'PhD': 5}
education_level_num = education_mapping[education_level]

# Encode 'Loan Purpose'
loan_purpose = st.selectbox('Loan Purpose', ['Home', 'Auto', 'Education', 'Personal' ])
loan_purpose_mapping = {'Home': 1, 'Auto': 2, 'Education': 3, 'Personal': 4}
loan_purpose_encoded = loan_purpose_mapping[loan_purpose]

credit_score = st.number_input('Credit Score', min_value=300, max_value=900)
loan_amount = st.number_input('Loan Amount', min_value=0)
loan_term_months = st.number_input('Loan Term (months)', min_value=1)
open_accounts = st.number_input('Number of Open Accounts', min_value=0)
outstanding_debt = st.number_input('Outstanding Debt', min_value=0)

dti = round(outstanding_debt / income * 100 , 2 )
# Create a button to make the predictions
if st.button('Predict Credit Worthiness'):
    # Prepare the input features as a NumPy array
    input_features = np.array([age, income, employment_years, education_level_num, loan_purpose_encoded, 
                               credit_score,loan_amount, loan_term_months, open_accounts,outstanding_debt,dti ])

    # Make predictions using the Random Forest model
    gb_prediction = gb_model.predict(input_features.reshape(1, -1))

    # Display the prediction
    if gb_prediction[0] == 1:
        st.write("Credit Worthiness: Approved")
    else:
        st.write("Credit Worthiness: Denied")


