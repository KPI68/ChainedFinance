// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Create a constructor for the KaseiCoin contract and have the contract inherit the libraries that you imported from OpenZeppelin.
contract Money {
    struct balance {
        uint snapshot;
        uint asat;
        uint aggregated;
        uint loan;        
    }

    mapping(address => balance) accounts ;

    function deposit() public payable {
        uint dys = ( block.timestamp - accounts[msg.sender].asat) / 60 / 60 / 24;
        accounts[msg.sender].aggregated = accounts[msg.sender].snapshot*dys;
        accounts[msg.sender].snapshot += msg.value;
        accounts[msg.sender].asat = block.timestamp;
    }

    function withdraw(uint amount) public payable {
        address payable recipient = payable(msg.sender) ;
        uint dys = ( block.timestamp - accounts[msg.sender].asat) / 60 / 60 / 24;
        require( address(this).balance> amount, "Not enough cash in system");
        require( accounts[recipient].snapshot> amount, "Not enough cash in account");
        accounts[recipient].aggregated = accounts[recipient].snapshot*dys;
        accounts[recipient].snapshot -= amount ;
        accounts[msg.sender].asat = block.timestamp;
        recipient.transfer(amount);
    }

    function cash_loan(uint amount) public payable {
        address payable recipient = payable(msg.sender) ;
        require( accounts[recipient].loan== 0, "Loan exists");
        require( address(this).balance> amount, "Not enough cash in system");
        accounts[recipient].loan = amount ;
        recipient.transfer(amount);
    }

    function repay_loan() public payable {
        require( accounts[msg.sender].loan>=msg.value, "Invalid loan amount" );
        accounts[msg.sender].loan -= msg.value;
    }

    function current_cash() public view returns(uint) {
        return accounts[msg.sender].snapshot;
    }

    function current_loan() public view returns(uint) {
        return accounts[msg.sender].loan;
    }

    function aggregated_balance() public view returns(uint) {
        return accounts[msg.sender].aggregated;
    }
}