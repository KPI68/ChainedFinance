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

    event Exposed(uint256 tokenId, string loan_uri);

    function getLoanDetails(uint256 tokenId) public view returns (string memory) {
        return loanCollection[tokenId].loan_uri;
    }

    function getLoanStartDate(uint256 tokenId) public view returns (string memory) {
        return loanCollection[tokenId].start_date;
    }

    function getLoanTenor(uint256 tokenId) public view returns (uint) {
        return loanCollection[tokenId].tenor;
    }

    function setLoanStartDate(uint256 tokenId, string memory start_date) public {
        loanCollection[tokenId].start_date = start_date;
    }   

    function setLoanTenor(uint256 tokenId, uint tenor) public {
        loanCollection[tokenId].tenor = tenor;
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

    function exposeDelinquent(
        uint256 tokenId
    ) public returns (string memory) {
        emit Exposed(tokenId, loanCollection[tokenId].loan_uri);

        return loanCollection[tokenId].loan_uri;
    }
} 