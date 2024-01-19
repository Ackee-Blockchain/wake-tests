// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "solady/src/tokens/ERC20.sol";

contract SoladyERC20 is ERC20 {
    constructor(uint256 initialSupply) {
        _mint(msg.sender, initialSupply);
    }

    function name() public view override returns (string memory) {
        return "SoladyToken";
    }

    function symbol() public view override returns (string memory) {
        return "SERC";
    }

    function decimals() public view override returns (uint8 dec) {
        assembly {
            dec := 18
        }
    }
}
