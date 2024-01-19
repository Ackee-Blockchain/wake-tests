// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "solmate/src/tokens/ERC20.sol";

contract SolmateERC20 is ERC20 {
    constructor(uint256 initialSupply)
    ERC20("SolmateToken", "SYERC", 18) {
        _mint(msg.sender, initialSupply);
    }
}
