// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Create a constructor for the KaseiCoin contract and have the contract inherit the libraries that you imported from OpenZeppelin.
contract Money {
    struct balance {
        uint snapshot;
        uint asat;
        uint aggregated;
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
        require( accounts[recipient].snapshot> amount, "Not enough money in account");
        accounts[recipient].aggregated = accounts[recipient].snapshot*dys;
        accounts[recipient].snapshot -= amount ;
        accounts[msg.sender].asat = block.timestamp;
        recipient.transfer(amount);
    }

    function current_balance() public view returns(uint) {
        return accounts[msg.sender].snapshot;
    }

    function aggregated_balance() public view returns(uint) {
        return accounts[msg.sender].aggregated;
    }
}