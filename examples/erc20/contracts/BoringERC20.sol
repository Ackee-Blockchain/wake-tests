// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@boringcrypto/boring-solidity/contracts/ERC20.sol";

contract BoringERC20 is ERC20WithSupply {
    string public constant name = "BoringToken";
    string public constant symbol = "BERC";

    constructor(uint256 initialSupply) {
        _mint(msg.sender, initialSupply);
    }
}
