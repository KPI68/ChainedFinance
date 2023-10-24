pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract LoanRegistry is ERC721Full {
    constructor() public ERC721Full("LoanToken", "LOAN") {}
    struct Loan {
        string start_date;
        uint tenor;    
        string loan_uri;    
    }
    mapping(uint256 => Loan) public loanCollection;

    function getLoanDetails(uint256 tokenId) public view returns (string memory, uint, string memory) {
        return (loanCollection[tokenId].start_date,
                loanCollection[tokenId].tenor,
                loanCollection[tokenId].loan_uri);
    }

    function updateLoan(
        uint256 tokenId,
        string memory start_date,
        uint tenor,
        string memory loan_uri
    ) public {

        loanCollection[tokenId] = Loan(start_date, tenor, loan_uri);
    }    

    function registerLoan(
        string memory start_date,
        uint tenor,
        string memory loan_uri
    ) public {
        uint256 tokenId = totalSupply();

        _mint(msg.sender, tokenId);
        _setTokenURI(tokenId, loan_uri);

        loanCollection[tokenId] = Loan(start_date, tenor, loan_uri);
    }    
} 