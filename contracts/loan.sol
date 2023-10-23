pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract LoanRegistry is ERC721Full {
    constructor() public ERC721Full("LoanToken", "LOAN") {}

    mapping(uint256 => string) public loanCollection;

    event Exposed(uint256 tokenId, string detailsJSON);

    function getLoanDetails(uint256 tokenId) public view returns (string memory) {
        return loanCollection[tokenId];
    }

    function registerLoan(
        string memory loan_url
    ) public returns (uint256) {
        uint256 tokenId = totalSupply();

        _mint(msg.sender, tokenId);
        _setTokenURI(tokenId, loan_url);

        loanCollection[tokenId] = loan_url;

        return tokenId;
    }    

    function exposeDelinquent(
        uint256 tokenId
    ) public returns (string memory) {
        emit Exposed(tokenId, loanCollection[tokenId]);

        return loanCollection[tokenId];
    }
} 