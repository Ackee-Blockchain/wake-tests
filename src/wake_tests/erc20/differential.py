from typing import Union
import warnings

from wake.testing import *

from .IERC20 import IERC20
from .mock import ERC20Mock
from .utils import (
    ZeroAddressWarning,
    IncorrectReturnValueWarning,
    ReturnInsteadOfRevertWarning,
    account_to_address_converter,
    all_events_emitted,
    decorate_all_functions,
)


@decorate_all_functions(account_to_address_converter)
class ERC20DifferentialTest:
    def __init__(self, erc20_token: IERC20, erc20_mock: ERC20Mock) -> None:
        self.erc20 = erc20_token
        self.erc20_mock = erc20_mock

    def mint(self, to: Union[Account, Address], amount: uint) -> None:
        if amount > 0:
            mint_erc20(self.erc20, to, amount)
            self.erc20_mock.mint(to, amount)

    ############################################################
    ### Differential testing with no known result in advance ###
    ############################################################

    def assert_approve(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
        should_zero_spender_fail: bool = False,
    ) -> None:
        if spender == Address.ZERO:
            self.assert_approve_zero_spender_valid(
                owner, amount, should_zero_spender_fail=should_zero_spender_fail
            )
        else:
            self.assert_approve_valid(owner, spender, amount)

    def assert_transfer(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        if receiver == Address.ZERO:
            self.check_transfer_to_zero_address(owner, amount)
        elif self.erc20_mock.should_transfer_succeed(owner, receiver, amount):
            self.assert_transfer_succeeds(owner, receiver, amount)
        else:
            self.assert_transfer_reverts(owner, receiver, amount)

    def assert_transferFrom(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        if receiver == Address.ZERO:
            self.assert_transferFrom_to_zero_address(owner, spender, amount)
        elif self.erc20_mock.should_transferFrom_succeed(
            owner, spender, receiver, amount
        ):
            self.assert_transferFrom_succeeds(owner, spender, receiver, amount)
        else:
            self.assert_transferFrom_reverts(owner, spender, receiver, amount)

    #########################################
    ### Validators of the expected result ###
    #########################################

    def assert_total_supply_matches_expected(self) -> None:
        assert self.erc20.totalSupply() == sum(
            self.erc20_mock.balances.values()
        ), "Incorrect totalSupply() value"

    def assert_transfer_succeeds(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transfer_success(owner, receiver, amount)

    def assert_transfer_reverts(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transfer_revert(owner, receiver, amount)

    def check_transfer_to_zero_address(
        self, owner: Union[Account, Address], amount: uint
    ) -> None:
        self._transfer_zero_recipient(owner, amount)

    def assert_approve_valid(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._approve(owner, spender, amount)

    def assert_approve_zero_spender_valid(
        self,
        owner: Union[Account, Address],
        amount: uint,
        should_zero_spender_fail: bool = False,
    ) -> None:
        self._approve_zero_spender(
            owner, amount, should_zero_spender_fail=should_zero_spender_fail
        )

    def assert_transferFrom_succeeds(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transferFrom_success(owner, spender, receiver, amount)

    def assert_transferFrom_reverts(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transferFrom_revert(owner, spender, receiver, amount)

    def assert_transferFrom_to_zero_address(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transferFrom_zero_recipient(owner, spender, amount)

    def assert_balances_match_expected(self) -> None:
        for account in default_chain.accounts:
            self._check_balance(account)

    def assert_allowances_match_expected(self) -> None:
        [
            self._check_allowance(o, s)
            for o in default_chain.accounts
            for s in default_chain.accounts
        ]

    ##################################################
    ### Functions that revert the blockchain state ###
    ##################################################

    def try_approve_and_restore(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
    ) -> bool:
        """This method tries to call the `approve` function and check the resulting allowance.
        If the allowance changed to value, the approval is meant to be successful, even if
        the return value is false or if the Approval event is not emitted."""
        with default_chain.snapshot_and_revert():
            try:
                self.erc20.approve(spender, amount, from_=owner)
                # skipping return value check, may be false for success
            except TransactionRevertedError:
                success = False
            else:
                allowance_after = self.erc20.allowance(owner, spender)
                success = allowance_after == amount
        return success

    def try_transfer_and_restore(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> bool:
        return self._try_transfer_transferFrom(owner, receiver, amount, spender=None)

    def try_transferFrom_and_restore(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> bool:
        return self._try_transfer_transferFrom(owner, receiver, amount, spender=spender)

    def _try_transfer_transferFrom(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        spender: Optional[Union[Account, Address]] = None,
    ) -> bool:
        """This method tries to call the transfer(From) function and check the resulting balances.
        If the balances changed by value, the transfer(From) is meant to be successful, even if
        the return value is false or if the Transfer event is not emitted.

        transfer is called is spender is None, otherwise transferFrom is called."""
        with default_chain.snapshot_and_revert():
            from_before = self.erc20.balanceOf(owner)
            to_before = self.erc20.balanceOf(receiver)
            try:
                if spender is not None:
                    self.erc20.transferFrom(owner, receiver, amount, from_=spender)
                else:
                    self.erc20.transfer(receiver, amount, from_=owner)
                # skipping return value check, may be false for success
            except TransactionRevertedError:
                success = False
            else:
                from_after = self.erc20.balanceOf(owner)
                to_after = self.erc20.balanceOf(receiver)
                success = (from_before - from_after) == amount == (to_after - to_before)
        return success

    #####################################################
    ### Validators of successful or failed operations ###
    #####################################################

    def _approve(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
        allow_zero_account: bool = False,
    ) -> None:
        tx = self.erc20.approve(spender, amount, from_=owner)
        exp_events = self.erc20_mock.approve(
            owner, spender, amount, allow_zero_account=allow_zero_account
        )
        if not tx.return_value:
            warnings.warn(
                f"Successful approve({owner=}, {spender=}, {amount=}) returned false",
                IncorrectReturnValueWarning,
            )
        assert all_events_emitted(
            tx.events, exp_events
        ), "No Approval event on successful approve"

    def _transfer_success(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        allow_zero_account: bool = False,
    ) -> None:
        tx = self.erc20.transfer(receiver, amount, from_=owner)
        exp_events = self.erc20_mock.transfer(
            owner, receiver, amount, allow_zero_account=allow_zero_account
        )
        if not tx.return_value:
            warnings.warn(
                f"Successful transfer(from={owner}, {receiver=}, {amount=}) returned false",
                IncorrectReturnValueWarning,
            )
        assert all_events_emitted(
            tx.events, exp_events
        ), "No Transfer event on successful transfer"

    def _transfer_revert(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        with may_revert():
            tx = self.erc20.transfer(receiver, amount, from_=owner)
            assert (
                tx.return_value == False
            ), f"Unsuccessful transfer(from={owner}, {receiver=}, {amount=}) neither reverted, nor returned false"
            # some contracts return false without revert
            warnings.warn(
                f"Unsuccessful transfer(from={owner}, {receiver=}, {amount=}) returned false. Consider using revert",
                ReturnInsteadOfRevertWarning,
            )
            # events must not contain Transfer in case of failure
            assert not all_events_emitted(
                tx.events, IERC20.Transfer(from_=owner, to=receiver, value=amount)
            ), "Transfer event emitted on unsuccessful transfer"

    def _transferFrom_success(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        allow_zero_account: bool = False,
    ) -> None:
        tx = self.erc20.transferFrom(owner, receiver, amount, from_=spender)
        exp_events = self.erc20_mock.transferFrom(
            owner,
            spender,
            receiver,
            amount,
            allow_zero_account=allow_zero_account,
        )
        if not tx.return_value:
            warnings.warn(
                f"Successful transferFrom({owner=}, {spender=}, {receiver=}, {amount=}) return false",
                IncorrectReturnValueWarning,
            )
        assert all_events_emitted(
            tx.events, exp_events
        ), "No Transfer event on successful transferFrom"

    def _transferFrom_revert(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        with may_revert():
            tx = self.erc20.transferFrom(owner, receiver, amount, from_=spender)
            assert (
                tx.return_value == False
            ), f"Unsuccessful transferFrom({owner=}, {spender=}, {receiver=}, {amount=}) neither reverted, nor returned false"
            # some contracts return false without revert
            warnings.warn(
                f"Unsuccessful transferFrom({owner=}, {spender=}, {receiver=}, {amount=}) returned false. Consider using revert",
                ReturnInsteadOfRevertWarning,
            )
            # events must not contain Transfer in case of failure
            assert not all_events_emitted(
                tx.events, IERC20.Transfer(from_=owner, to=receiver, value=amount)
            ), "Transfer event emitted on unsuccessful transferFrom"

    ###############################
    ### Zero address validators ###
    ###############################

    def _approve_zero_spender(
        self,
        owner: Union[Account, Address],
        amount: uint,
        should_zero_spender_fail: bool = False,
    ) -> None:
        """Try to approve spending by the zero address.

        The standard does not define the behavior of this, however, successful
        approvals are not recommended. This test will warn you if the approval
        is successful, however, it also checks if Approval is emitted."""

        # We cannot trust the contract nor with the return value, neither with revert,
        # and ERC-20 does not define the exact behavior of approvals for 0x0. Furthermore,
        # the fact of the emitted Approval event cannot serve as a proof neither, it may
        # be a mistake. Thus, we have to guess by the change of allowances.
        spender = Address.ZERO

        # Find out if the contract allows spender=0x0 (value should differ from the actual one)
        approve_succeeds = self.try_approve_and_restore(owner, spender, amount)
        assert not (
            approve_succeeds and should_zero_spender_fail
        ), "approve(0x0) succeeded but should not"

        if approve_succeeds:
            # 0x0 approvals are allowed, proceed with additional checks and warn
            self._approve(owner, spender, amount, allow_zero_account=True)
            warnings.warn(
                f"approve({owner=}, {spender=}, {amount=}) succeeded",
                ZeroAddressWarning,
            )
        else:
            # 0x0 approvals are not allowed, good
            pass

    def _transfer_zero_recipient(
        self, owner: Union[Account, Address], amount: uint
    ) -> None:
        self._transfer_transferFrom_zero_recipient(owner, amount)

    def _transferFrom_zero_recipient(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
    ) -> None:
        self._transfer_transferFrom_zero_recipient(owner, amount, spender=spender)

    def _transfer_transferFrom_zero_recipient(
        self,
        owner: Union[Account, Address],
        amount: uint,
        spender: Optional[Union[Account, Address]] = None,
    ) -> None:
        # We cannot trust the contract nor with the return value, neither with revert,
        # and ERC-20 does not define the exact behavior of transfers to 0x0. Furthermore,
        # the fact of the emitted Transfer event cannot serve as a proof neither, it may
        # be a mistake. Thus, we have to guess by the change of balances. However, if
        # value=0, the behavior is completely implementation dependent.
        receiver = Address.ZERO

        # First, a sanity check, whether the passed values are valid
        if spender is not None:
            should_succeed = self.erc20_mock.should_transferFrom_succeed(
                owner,
                spender,
                receiver,
                amount,
                allow_zero_account=True,
            )
            transfer_succeeds = self.try_transferFrom_and_restore(
                owner, spender, receiver, amount
            )
            fn_success = self._transferFrom_success
            fn_revert = self._transferFrom_revert
            args = (owner, spender, receiver, amount)
            kwargs = dict()
            signature = f"transferFrom({owner=}, {spender=}, {receiver=}, {amount=})"
        else:
            should_succeed = self.erc20_mock.should_transfer_succeed(
                owner, receiver, amount, allow_zero_account=True
            )
            # We need to find out if the contract reverts on to=0x0
            transfer_succeeds = self.try_transfer_and_restore(owner, receiver, amount)
            fn_success = self._transfer_success
            fn_revert = self._transfer_revert
            args = (owner, receiver, amount)
            kwargs = dict()
            signature = f"transfer(from={owner}, {receiver=}, {amount=})"

        if should_succeed and transfer_succeeds:
            # we know that the transaction does not revert
            fn_success(*args, **kwargs, allow_zero_account=True)
            # emit warning, 0x0 should revert
            warnings.warn(f"{signature} succeeded", ZeroAddressWarning)
        elif should_succeed and not transfer_succeeds:
            # in this case, transfer with to=0x0 reverted, which is good
            # proceed with basic checks (events, return value)
            fn_revert(*args, **kwargs)
        elif not should_succeed and transfer_succeeds:
            # clearly, something is wrong, we proceed with the expected revert
            fn_revert(*args, **kwargs)
        else:
            # should not succeed, nor succeeded, everything's good
            # proceed with the basic checks
            fn_revert(*args, **kwargs)

    ########################################
    ### Balance and allowance validators ###
    ########################################

    def _check_balance(self, account: Union[Account, Address]) -> None:
        expected = self.erc20_mock.balanceOf(account)
        got = self.erc20.balanceOf(account)
        assert (
            got == expected
        ), f"Incorrect balanceOf({account=}) value. Expected: {expected}, got: {got}"

    def _check_allowance(
        self, owner: Union[Account, Address], spender: Union[Account, Address]
    ) -> None:
        expected = self.erc20_mock.allowance(owner, spender)
        got = self.erc20.allowance(owner, spender)
        assert (
            got == expected
        ), f"Incorrect allowance({owner=}, {spender=}). Expected: {expected}, got: {got}"
