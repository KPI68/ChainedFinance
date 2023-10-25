// SPDX-License-Identifier: MIT
pragma solidity ^0.5.0;

// Create a constructor for the KaseiCoin contract and have the contract inherit the libraries that you imported from OpenZeppelin.
contract Money {
    struct balance {
        uint snapshot;
        uint asat;
        uint aggregated;
        uint loan;    
        uint loan_id;    
    }

    mapping(address => balance) accounts ;
    uint total_loan;
    uint total_interest;
    uint current_rate;
    uint collector_rate;

    function deposit() public payable {
        uint dys = ( block.timestamp - accounts[msg.sender].asat) / 60 / 60 / 24;
        accounts[msg.sender].aggregated += accounts[msg.sender].snapshot*dys;
        accounts[msg.sender].snapshot += msg.value;
        accounts[msg.sender].asat = block.timestamp;
    }

    function withdraw(uint amount) public payable {
        address payable recipient = msg.sender ;
        uint dys = ( block.timestamp - accounts[msg.sender].asat) / 60 / 60 / 24;
        require( address(this).balance> amount, "Not enough cash in system");
        require( accounts[recipient].snapshot> amount, "Not enough cash in account");
        accounts[recipient].aggregated += accounts[recipient].snapshot*dys;
        accounts[recipient].snapshot -= amount ;
        accounts[msg.sender].asat = block.timestamp;
        recipient.transfer(amount);
    }

    function cash_loan(uint amount) public payable {
        address payable recipient = msg.sender ;
        require(address(this).balance> amount, "Not enough cash in system");
        accounts[recipient].loan += amount ;
        total_loan += amount;
        recipient.transfer(amount);
    }

    function repay_loan() public payable {
        require(accounts[msg.sender].loan>=msg.value, "Invalid loan amount" );
        accounts[msg.sender].loan -= msg.value;
        total_loan -= msg.value;
    }

    function repay_interest() public payable {
        total_interest += msg.value;
    }

    function cash_interest(uint amount) public payable {
        address payable recipient = msg.sender;
        require(total_interest> amount, "Not enough interest received in system");
        accounts[recipient].aggregated = 0;
        total_interest -= amount;
        recipient.transfer(amount);
    }

    function current_cash() public view returns(uint) {
        return accounts[msg.sender].snapshot;
    }

    function current_loan() public view returns(uint) {
        return accounts[msg.sender].loan;
    }

    function get_total_loan() public view returns(uint) {
        return total_loan;
    }

    function current_interest() public view returns(uint) {
        uint dys = ( block.timestamp - accounts[msg.sender].asat) / 60 / 60 / 24;
        uint aggregated_to_day = accounts[msg.sender].aggregated + accounts[msg.sender].snapshot*dys;
        return aggregated_to_day * current_rate / 365000;
    }

    function get_total_interest() public view returns(uint) {
        return total_interest;
    }

    function set_rate(uint rate) public {
        current_rate = (current_rate* (address(this).balance - accounts[msg.sender].snapshot) + 
            rate*accounts[msg.sender].snapshot) / address(this).balance; 
    }

    function get_rate() public view returns(uint) {
        return current_rate;
    }

    function set_collector_rate(uint rate) public {
        collector_rate = rate;
    }

    function get_collector_rate() public view returns(uint) {
        return collector_rate;
    }

    function set_loan_id(uint id) public {
        accounts[msg.sender].loan_id = id;
    }

    function get_loan_id() public view returns(uint) {
        return accounts[msg.sender].loan_id;
    }
}