# ChainedFinance

Welcome to a a peer-to-peer lending platform powered via blockchain technology and machine learning. A powerful , secure and versatile tool designed to empower users to interact with Ethereum smart contracts to lend and borrow money. 

### Key Achievements:

**Financial Empowerment:** This project seeks to empower users by simplifying complex financial transactions on the Ethereum blockchain. You can securely and easily perform essential tasks such as depositing funds to the system and borrowing, repaying, and renewing loans.

**Transparency:** The project promotes transparency by leveraging blockchain technology. Users can access and verify financial data and transaction records on the Ethereum blockchain.

**Flexibility:** Depending upon individual needs the project helps achieve a wide range of financial functionalities. It adapts to your unique financial needs and allows you to manage your funds effectively.

**Educational Tool:** This project serves as an educational tool, offering insights into how blockchain-based financial applications work. Users can explore and experiment with various financial operations in a safe and controlled environment.

**Quality Assurance:** The project has undergone quality assurance testing to ensure that it functions as expected and delivers a seamless user experience. 

### Prerequisites

Before running the application, make sure you have the following prerequisites installed on your machine:

* Ganache or a local Ethereum blockchain for development and testing
* Create a .env file in the project directory and configure the following environment variables:
    
    * WEB3_PROVIDER_URI=HTTP://127.0.0.1:7545 (For Ganache Only)
    * ACC_CONTRACT_ADDRESS=
    * LOAN_CONTRACT_ADDRESS=
    * PINATA_API_KEY=
    * PINATA_SECRET_API_KEY=


### Using the App

Once the application is running, you can interact with it using the following functions:

**Deposit:** Deposit Ether into your account and propose an annual interest rate.
**Withdraw:** Withdraw Ether from your account. System will only allow withdrawal if you have enough funds available.
**Apply Loan:** Apply for a loan. Specify the number of ETH you wish to borrow , tenure of the loan , fill out your personal and financial information and let the machine learning model predict your credit worthiness. Your personal details are stored on an external "Decentralized File Hosting" system called "Pinata" and loan information is stored on the blockchain.
**Repay Loan:** Repay an existing loan, including accrued interest.
**Renew Loan:** Renew an existing loan with a new allowance and tenure.
**Request Interest:** Request earned interest from your account.
**Collector:** View current commission rates and list delinquent loans.

Follow the on-screen instructions for each function and input the required information. You can select your Ethereum account address from the dropdown menu.

The application provides metrics on your account's total cash, total loans, and total interest in real-time. These metrics are displayed at the top of the application.

### Important Notes

This application assumes that you have deployed and configured the Account and Loan smart contracts on your test Ethereum blockchain. Ensure that the contract addresses and the Web3 provider URI are correctly configured in the .env file.

The application may require the Metamask browser extension to connect to your Ethereum account, especially if you are using a browser-based Ethereum wallet.

This app is for educational and testing purposes and is not intended for production use.

Feel free to explore the application and experiment with different financial operations on the Ethereum blockchain.


## Quality Assurance 

### Step by Step instruction for functionality test.

1. **Deposit Funds:**

* Select your ethereum account address.
* Select the "Deposit" function from the dropdown.
* Enter the amount of Ether you want to deposit in the "Number of ETH" field. The system will calculate and show the CAD equivalent in real time.
* Propose an annual interest rate by moving the slider.
* Click the "Submit" button.

**Expected Outcome:** The application should deposit the specified amount of Ether, out from your Ethereum wallet, into your account. You should see a transaction receipt and updated metrics for "Total Cash."

2. **Withdraw Funds:**

* Select your ethereum account address.
* Select the "Withdraw" function from the dropdown.
* The current balance in Ether should be displayed. Enter the amount of Ether you want to withdraw in the "Number of ETH" field.
* Click the "Submit" button.

**Expected Outcome:** The application should withdraw the specified amount of Ether from your account. You should see a transaction receipt and updated metrics for "Total Cash". The withdrawn amount lands in your Ethereum wallet.

3. **Apply for a Loan:**

* Select your ethereum account address.
* Select the "Apply Loan" function from the dropdown.
* Enter the desired allowance or sum you wish to borrow in Ether in the "Number of ETH" field.
* Adjust the tenure by moving the slider.
* Fill out your personal and financial information including uploading a copy of your ID.
* Click the "Submit" button.

**Expected Outcome:** The application should create a loan based on the specified allowance and tenure given the machine learning model approves the client for a loan. You should see a the loan amount approved in ether and a loan details link that will display the details of the client, and the loan amount land in your Ethereum wallet, if approved.

4. **Repay a Loan:**

* Select your ethereum account address.
* Select the "Repay Loan" function from the dropdown.
* The application will automatically display your loan details.
* Enter the amount of Ether you want to repay in the "Number of ETH" field.
* Click the "Submit" button.

**Expected Outcome:** The application should accept the repayment, update your loan status, and repay the principal and interest out of your Ethereum wallet. The interest is calculated with amount repaid, days since borrow and current system rate.

5. **Renew a Loan:**

* Select your ethereum account address.
* Select the "Renew Loan" function from the dropdown.
* The application will automatically display your loan details.
* Enter the new allowance in Ether in the "Number of ETH" field.
* Adjust the tenure by moving the slider.
* Click the "Submit" button.

**Expected Outcome:** The application should renew your loan with the new allowance and tenure. You should see a transaction receipt, and your loan details should be updated. At renewal, the full interest out of previous loan amount is paid out from your Ethereum wallet. If renewal requiring less, partial repay happens out of your wallet; If renewal requiring more, the extra amount is transfered to your Ethereum wallet.

6. **Collector:**

* Select the "Collector" function from the dropdown.
The application should display the current commission rate and allow you to list delinquent loans.

**Expected Outcome:** The application should display the commission rate and provide options to view and take action on delinquent loans.

7. **Request Interst:**

* Select the "Request Interest" function from the dropdown.
* The application will automatically display your deposit balance and interest earned to date
* The interest earned to date is calculated from your account aggregated balance since deposit and current system rate
* Click the "Submit" button.

**Expected Outcome:** The application should send the interest in full amount to your Ethereum wallet.

![before](Images/before_request_interest_0x481.png)

![request_interest](Images/request_interest_0x481.png)

![after](Images/after_reqeust_interest_0x481.png)
