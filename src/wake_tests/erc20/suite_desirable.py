import warnings

import pytest

from wake.testing import *

from .utils import UINT256_MAX
from .suite_abc import ERC20Base


class ERC20Desirable(ERC20Base):
    """Tests of level **Desirable** check properties we deem important to the sane
    functioning of a token and complement the standard specification.

    Some of these properties were violated in ERC-20 hacks. Examples of desirable
    properties include (i) self-transferring tokens is allowed but must not modify
    the balance (ii) increase of allowance should rely on an `increaseAllowance`
    function.
    """

    @default_chain.connect()
    def test_address_zero_has_no_token(self):
        """The zero address SHOULD NOT have any token from the contract."""
        self.setup_contract()
        with may_revert():
            balance = self.erc20.balanceOf(Address.ZERO)
            assert balance == 0, "The zero address has a non-zero balance."

    @default_chain.connect()
    def test_balance_of_caller(self):
        """A `msg.sender` SHOULD be able to retrieve his/her own balance."""
        self.setup_contract()
        account = default_chain.accounts[0]
        balance_self = self.erc20.balanceOf(account, from_=account)
        assert isinstance(balance_self, int), "Balance is not an integer."

    @default_chain.connect()
    def test_balance_of_non_caller(self):
        """A `msg.sender` SHOULD be able to retrieve balance of an address different from his/hers."""
        self.setup_contract()
        account = default_chain.accounts[0]
        another_account = default_chain.accounts[1]
        balance_other = self.erc20.balanceOf(another_account, from_=account)
        assert isinstance(balance_other, int), "Balance is not an integer."

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="Approvals to the zero address may be allowed but it is not recommended."
    )
    def test_cannot_approve_positive_amount_to_zero_address(self):
        """A successful call of `approve` of any amount to the zero address SHOULD NOT be allowed."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_approve_zero_spender_valid(
            account_owner, 0, should_zero_spender_fail=True
        )
        self.assert_approve_zero_spender_valid(
            account_owner, 1, should_zero_spender_fail=True
        )
        self.assert_approve_zero_spender_valid(
            account_owner, UINT256_MAX, should_zero_spender_fail=True
        )
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_fee_taking_transferFrom_present(self):
        """The `transferFrom` function DOES NOT take fees at test execution time."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, amount
        )

        self.assert_allowances_match_expected()
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_fee_taking_transfer_present(self):
        """The `transfer` function DOES NOT take fees at test execution time."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, amount)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_multiple_transferFrom_exceed_allowance(self):
        """Multiple calls of `transferFrom` SHOULD NOT be allowed once allowance reach zero even if the tokenSender's balance is more than the allowance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        amount = 100
        send_amount = 50

        # Fully approve
        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, send_amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        # Partially approve
        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, send_amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_allowances_match_expected()
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_overwrite_approve_positive_to_zero(self):
        """Consecutive calls of `approve` function of positive-to-zero amounts CAN be called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]

        self.assert_approve_valid(account_owner, account_spender, 10)
        self.assert_approve_valid(account_owner, account_spender, 0)

        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_overwrite_approve_zero_to_positive(self):
        """Consecutive calls of `approve` function of zero-to-positive amounts CAN be called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]

        self.assert_approve_valid(account_owner, account_spender, 0)
        self.assert_approve_valid(account_owner, account_spender, 10)

        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_overwrite_approve_zero_to_zero(self):
        """Consecutive calls of `approve` function of zero-to-zero amounts CAN be called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]

        self.assert_approve_valid(account_owner, account_spender, 0)
        self.assert_approve_valid(account_owner, account_spender, 0)

        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_multiple_transfer(self):
        """Multiple `transfer` calls of positive amounts are ALLOWED given that the sum of the transferred amounts is less than or equal to the tokenSender's balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100
        send_amount = 50

        self.mint(account_owner, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, send_amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, send_amount)
        self.assert_transfer_reverts(account_owner, account_receiver, send_amount)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_positive_multiple_transferFrom(self):
        """Multiple `transferFrom` calls of positive amounts are ALLOWED given that the sum of the transferred amounts is less than or equal to the tokenSender's balance and approvals are given by the tokenSender."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        amount = 100
        approve_amount = 200
        send_amount = 50

        # Fully approve
        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, approve_amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_self_approve(self):
        """Self-approval of positive amount is ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        amount = 100

        self.assert_approve_valid(account_owner, account_owner, amount)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_self_approve_transferFrom(self):
        """Self-approval and call of `transferFrom` from its own account of positive amount is ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_owner, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_owner, amount
        )

        self.assert_balances_match_expected()

        try:
            self.assert_allowances_match_expected()
        except AssertionError:
            warnings.warn(
                "The allowance of the tokenSender SHOULD be decreased by the amount of the transfer even if the tokenSender and the tokenReceiver are the same address."
            )

    @default_chain.connect()
    def test_positive_self_transfer(self):
        """Self `transfer` call of positive amount is ALLOWED and SHOULD NOT modify the balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transfer_succeeds(account_owner, account_owner, amount)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_positive_total_transferFrom_to_other(self):
        """A tokenReceiver CAN call `transferFrom` of the tokenSender's total balance amount given that tokenSender has approved that."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_receiver, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_receiver, account_receiver, amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_total_transfer_to_other(self):
        """A `msg.sender` CAN call `transfer` of her total balance amount to a tokenReceiver."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, amount)

        self.assert_balances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="Transfers to the zero address may be allowed but it is not recommended."
    )
    def test_positive_transferFrom_to_zero_should_revert(self):
        """A `transferFrom` call of any positive amount to the zero address SHOULD revert."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, Address.ZERO, amount
        )
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, Address.ZERO, amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="Transfers to the zero address may be allowed but it is not recommended."
    )
    def test_positive_transfer_to_zero_should_revert(self):
        """A `transfer` call of any positive amount to the zero address SHOULD revert."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transfer_reverts(account_owner, Address.ZERO, 1)
        self.assert_transfer_reverts(account_owner, Address.ZERO, amount)
        self.assert_transfer_reverts(account_owner, Address.ZERO, UINT256_MAX)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_total_supply_constant_after_transfer(self):
        """The contract's `totalSupply` variable SHOULD NOT be altered after `transfer` is called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, amount)

        self.assert_total_supply_matches_expected()

    @default_chain.connect()
    def test_total_supply_constant_after_transferFrom(self):
        """The contract's `totalSupply` variable SHOULD NOT be altered after `transferFrom` is called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, amount
        )

        self.assert_total_supply_matches_expected()

    @default_chain.connect()
    def test_transfer_does_not_update_others_balances(self):
        """A successful call of `transfer` DOES NOT update the balance of users who are neither the tokenSender nor the tokenReceiver."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        account_other = default_chain.accounts[2]
        amount = 100

        self.mint(account_owner, amount)
        self.mint(account_other, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver, amount)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_transferFrom_decrease_allowance_as_expected(self):
        """A successful `transferFrom` of any positive amount MUST decrease the allowance of the tokenSender by the transferred amount."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        amount = 100

        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_transferFrom_does_not_update_others_balances(self):
        """A successful call of `transferFrom` DOES NOT update the balance of users who are neither the tokenSender nor the tokenReceiver."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        account_other = default_chain.accounts[3]
        amount = 100

        self.mint(account_owner, amount)
        self.mint(account_other, amount)
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_address_cannot_approve_positive_amount(self):
        """A `approve` call of any positive amount SHOULD revert if the tokenSender is the zero address."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_approve_zero_spender_valid(
            account_owner, 0, should_zero_spender_fail=False
        )
        self.assert_approve_zero_spender_valid(
            account_owner, 1, should_zero_spender_fail=False
        )
        self.assert_approve_zero_spender_valid(
            account_owner, UINT256_MAX, should_zero_spender_fail=False
        )

        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_multiple_transfer(self):
        """Multiple calls of `transfer` of zero amount are ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]

        self.assert_transfer_succeeds(account_owner, account_receiver, 0)
        self.assert_transfer_succeeds(account_owner, account_receiver, 0)
        self.assert_transfer_succeeds(account_owner, account_owner, 0)
        self.assert_transfer_succeeds(account_owner, account_owner, 0)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_zero_multiple_transferFrom(self):
        """Multiple calls of `transferFrom` of zero amount are ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]

        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )

        self.assert_approve_valid(account_owner, account_spender, 100)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_self_approve(self):
        """Self-approval of zero amount is ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_approve_valid(account_owner, account_owner, 0)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_self_approve_transferFrom(self):
        """Self-approval and call of `transferFrom` from its own account of zero amount is ALLOWED."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_approve_valid(account_owner, account_owner, 0)
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_owner, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_self_transfer(self):
        """Self `transfer` call of zero amount is ALLOWED and SHOULD NOT modify the balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_transfer_succeeds(account_owner, account_owner, 0)

        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_zero_total_transferFrom_to_other(self):
        """A tokenReceiver CAN call `transferFrom` of the tokenSender's total balance amount of zero."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]

        self.assert_approve_valid(account_owner, account_spender, 0)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_total_transfer_to_other(self):
        """A `msg.sender` CAN call `transfer` of her total balance amount of zero to a tokenReceiver."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]

        self.assert_transfer_succeeds(account_owner, account_receiver, 0)

        self.assert_balances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="Transfer of zero amount to the zero address may be allowed but it is not recommended."
    )
    def test_zero_transferFrom_to_zero_should_revert(self):
        """A `transferFrom` call of zero amount to the zero address SHOULD revert."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]

        self.assert_approve_valid(account_owner, account_spender, 0)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, Address.ZERO, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="Transfer of zero amount to the zero address may be allowed but it is not recommended."
    )
    def test_zero_transfer_to_zero_should_revert(self):
        """A `transfer` call of zero amount to the zero address SHOULD revert."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_transfer_reverts(account_owner, Address.ZERO, 0)

        self.assert_balances_match_expected()
