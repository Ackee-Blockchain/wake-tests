import warnings
import inspect
import pytest

from wake.testing import *

from .utils import selector, keccak256_hash
from .suite_abc import ERC20Base


class ERC20Abi(ERC20Base):
    """Tests of level **ABI** check the name, inputs, and outputs of the token functions."""

    @default_chain.connect()
    def test_allowance_abi(self):
        """The `allowance(address,address)` function conforms to the EIP-20 standard:

        Signature: function allowance(address, address) public view returns (uint256 remaining)

        This test assumes the token is represented by a pytypes class.
        """
        self.setup_contract()
        fn_selector = selector("allowance(address,address)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The allowance(address,address) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert len(inputs) == 2 and all(
            i["internalType"] == "address" for i in inputs
        ), "Allowance should have exactly two arguments of type address."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "uint256"
        ), "Allowance should have exactly one output of type uint256."

    @default_chain.connect()
    def test_allowance_signature(self):
        """The `allowance(address,address)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("allowance(address,address)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The allowance(address,address) selector is not present in the ABI."

    @default_chain.connect()
    def test_approval_event_signature(self):
        """The `Approval(address,address,uint256)` event is present in the contract.

        Signature: event Approval(address indexed _owner, address indexed _spender, uint256 _value)
        """
        self.setup_contract()
        approval = getattr(self.token, "Approval")
        assert hasattr(
            self.token, "Approval"
        ), "The Approval event is not present in the contract."
        assert inspect.isclass(
            getattr(self.token, "Approval")
        ), "The Approval event is not a class."
        reference_selector = keccak256_hash("Approval(address,address,uint256)")
        assert approval.selector == reference_selector, (
            "The Approval event signature does not match the reference signature."
            f" Expected {reference_selector}, got {approval.selector}"
        )

        # we already know the selector is correct, so we can check the indexed arguments
        inputs = approval._abi["inputs"]
        assert (
            inputs[0]["indexed"] and inputs[1]["indexed"]
        ), "The Approval event should have two indexed arguments."

    @default_chain.connect()
    def test_approve_abi(self):
        """The `approve(address,uint256)` function conforms to the EIP-20 standard.

        Signature: function approve(address, uint256) public returns (bool success)
        """
        self.setup_contract()
        fn_selector = selector("approve(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The approve(address,uint256) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 2
            and inputs[0]["internalType"] == "address"
            and inputs[1]["internalType"] == "uint256"
        ), "Approve should have exactly two arguments of type address and uint256."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "bool"
        ), "Approve should have exactly one output of type bool."

    @default_chain.connect()
    def test_approve_signature(self):
        """The `approve(address,uint256)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("approve(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The approve(address,uint256) selector is not present in the ABI."

    @default_chain.connect()
    def test_balanceOf_abi(self):
        """The `balanceOf(address)` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("balanceOf(address)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The balanceOf(address) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 1 and inputs[0]["internalType"] == "address"
        ), "BalanceOf should have exactly one argument of type address."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "uint256"
        ), "BalanceOf should have exactly one output of type uint256."

    @default_chain.connect()
    def test_balanceOf_signature(self):
        """The `balanceOf(address)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("balanceOf(address)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The balanceOf(address) selector is not present in the ABI."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="decimals() is optional, however, it is recommended to implement it."
    )
    def test_decimals_abi(self):
        """The `decimals()` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("decimals()")
        abi = self.token._abi
        assert fn_selector in abi, "The decimals() selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert len(inputs) == 0, "Decimals should have no arguments."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "uint8"
        ), "Decimals should have exactly one output of type uint8."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="decimals() is optional, however, it is recommended to implement it."
    )
    def test_decimals_signature(self):
        """The `decimals()` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("decimals()")
        abi = self.token._abi
        assert fn_selector in abi, "The decimals() selector is not present in the ABI."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="decimals() is optional, however, it is recommended to implement it."
    )
    def test_decimals(self):
        """The `decimals()` function returns the correct value."""
        self.setup_contract()
        decimals = self.erc20.decimals()
        assert (
            isinstance(decimals, int) and 0 < decimals < 77
        ), "Decimals should be between 0 and 77"

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="name() is optional, however, it is recommended to implement it."
    )
    def test_name_abi(self):
        """The `name()` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("name()")
        abi = self.token._abi
        assert fn_selector in abi, "The name() selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert len(inputs) == 0, "Name should have no arguments."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "string"
        ), "Name should have exactly one output of type string."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="name() is optional, however, it is recommended to implement it."
    )
    def test_name_signature(self):
        """The `name()` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("name()")
        abi = self.token._abi
        assert fn_selector in abi, "The name() selector is not present in the ABI."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="symbol() is optional, however, it is recommended to implement it."
    )
    def test_symbol_abi(self):
        """The `symbol()` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("symbol()")
        abi = self.token._abi
        assert fn_selector in abi, "The symbol() selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert len(inputs) == 0, "Symbol should have no arguments."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "string"
        ), "Symbol should have exactly one output of type string."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="symbol() is optional, however, it is recommended to implement it."
    )
    def test_symbol_signature(self):
        """The `symbol()` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("symbol()")
        abi = self.token._abi
        assert fn_selector in abi, "The symbol() selector is not present in the ABI."

    @default_chain.connect()
    def test_totalSupply_abi(self):
        """The `totalSupply()` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("totalSupply()")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The totalSupply() selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert len(inputs) == 0, "TotalSupply should have no arguments."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "uint256"
        ), "TotalSupply should have exactly one output of type uint256."

    @default_chain.connect()
    def test_totalSupply_signature(self):
        """The `totalSupply()` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("totalSupply()")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The totalSupply() selector is not present in the ABI."

    @default_chain.connect()
    def test_transfer_abi(self):
        """The `transfer(address,uint256)` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("transfer(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The transfer(address,uint256) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 2
            and inputs[0]["internalType"] == "address"
            and inputs[1]["internalType"] == "uint256"
        ), "Transfer should have exactly two arguments of type address and uint256."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "bool"
        ), "Transfer should have exactly one output of type bool."

    @default_chain.connect()
    def test_transfer_event_signature(self):
        """The `Transfer(address,address,uint256)` event is present in the contract."""
        self.setup_contract()
        transfer = getattr(self.token, "Transfer")
        assert hasattr(
            self.token, "Transfer"
        ), "The Transfer event is not present in the contract."
        assert inspect.isclass(
            getattr(self.token, "Transfer")
        ), "The Transfer event is not a class."
        reference_selector = keccak256_hash("Transfer(address,address,uint256)")
        assert transfer.selector == reference_selector, (
            "The Transfer event signature does not match the reference signature. "
            f"Expected {reference_selector}, got {transfer.selector}"
        )

        # we already know the selector is correct, so we can check the indexed arguments
        inputs = transfer._abi["inputs"]
        assert (
            inputs[0]["indexed"] and inputs[1]["indexed"]
        ), "The Transfer event should have two indexed arguments."

    @default_chain.connect()
    def test_transferFrom_abi(self):
        """The `transferFrom(address,address,uint256)` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("transferFrom(address,address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The transferFrom(address,address,uint256) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 3
            and inputs[0]["internalType"] == "address"
            and inputs[1]["internalType"] == "address"
            and inputs[2]["internalType"] == "uint256"
        ), "TransferFrom should have exactly three arguments of type address, address, and uint256."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "bool"
        ), "TransferFrom should have exactly one output of type bool."

    @default_chain.connect()
    def test_transferFrom_signature(self):
        """The `transferFrom(address,address,uint256)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("transferFrom(address,address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The transferFrom(address,address,uint256) selector is not present in the ABI."

    @default_chain.connect()
    def test_transfer_signature(self):
        """The `transfer(address,uint256)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("transfer(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The transfer(address,uint256) selector is not present in the ABI."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="The increaseAllowance(address,uint256) function is not a part of the ERC-20 standard."
    )
    def test_increaseAllowance_abi(self):
        """The `increaseAllowance(address,uint256)` function is present in the contract."""
        self.setup_contract()
        fn_selector = selector("increaseAllowance(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The increaseAllowance(address,uint256) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 2
            and inputs[0]["internalType"] == "address"
            and inputs[1]["internalType"] == "uint256"
        ), "IncreaseAllowance should have exactly two arguments of type address and uint256."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "bool"
        ), "IncreaseAllowance should have exactly one output of type bool."

        warnings.warn(
            "The increaseAllowance(address,uint256) function is not a part of the ERC-20 standard"
            "and was deprecated by OpenZeppelin. Consider removing it from your contract.",
            DeprecationWarning,
        )

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="The decreaseAllowance(address,uint256) function is not a part of the ERC-20 standard."
    )
    def test_decreaseAllowance_abi(self):
        """The `decreaseAllowance(address,uint256)` function conforms to the EIP-20 standard."""
        self.setup_contract()
        fn_selector = selector("decreaseAllowance(address,uint256)")
        abi = self.token._abi
        assert (
            fn_selector in abi
        ), "The decreaseAllowance(address,uint256) selector is not present in the ABI."
        inputs = abi[fn_selector]["inputs"]
        assert (
            len(inputs) == 2
            and inputs[0]["internalType"] == "address"
            and inputs[1]["internalType"] == "uint256"
        ), "DecreaseAllowance should have exactly two arguments of type address and uint256."
        outputs = abi[fn_selector]["outputs"]
        assert (
            len(outputs) == 1 and outputs[0]["internalType"] == "bool"
        ), "DecreaseAllowance should have exactly one output of type bool."

        warnings.warn(
            "The decreaseAllowance(address,uint256) function is not a part of the ERC-20 standard"
            " and was deprecated by OpenZeppelin. Consider removing it from your contract.",
            DeprecationWarning,
        )
