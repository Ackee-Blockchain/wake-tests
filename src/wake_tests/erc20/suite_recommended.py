import pytest

from wake.testing import *

from .suite_abc import ERC20Base


class ERC20Recommended(ERC20Base):
    """Tests of level **Recommended** check the properties that SHOULD be respected.

    Note that the properties tested by `testDefaultOverwriteApprove` and
    `testRecommendedOverwriteApprove` are exclusive of each other and
    hence the tests cannot both pass.
    """

    @default_chain.connect()
    def test_cannot_transferFrom_more_than_allowance_lower_than_balance(self):
        """A tokenReceiver SHOULD NOT be able to call `transferFrom` of an amount more than her allowance from the tokenSender even if the tokenSender's balance is more than or equal to the said amount."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 200
        allowance = 100
        send_amount = 150

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_cannot_transferFrom_more_than_balance_but_lower_than_allowance(self):
        """A tokenReceiver SHOULD NOT be able to call `transferFrom` of an amount more than the tokenSender's balance even if the tokenReceiver's allowance from the tokenSender is more than the said amount."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 200
        allowance = 300
        send_amount = 250

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_cannot_transfer_more_than_balance(self):
        """A tokenSender (which is also the `msg.sender`) SHOULD NOT be able to call `transfer` of an amount more than his balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        balance = 200
        send_amount = 250

        self.mint(account_owner, balance)
        self.assert_transfer_reverts(account_owner, account_receiver, send_amount)
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_no_approval_cannot_transferFrom(self):
        """A tokenReceiver SHOULD NOT be able to call `transferFrom` of any positive amount from an tokenSender if the tokenSender did not approve the tokenReceiver previously."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 200
        send_amount = 100

        self.mint(account_owner, balance)
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(
        reason="transferFrom() from self by self SHOULD revert without self-approval but it is not a part of the standard."
    )
    def test_no_self_approval_cannot_self_transferFrom(self):
        """A `msg.sender` SHOULD NOT be able to call `transferFrom` of any positive amount from his/her own account to any tokenReceiver if the `msg.sender` did not approve him/herself prior to the call."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        balance = 200
        send_amount = 100

        self.mint(account_owner, balance)
        self.assert_transferFrom_reverts(
            account_owner, account_owner, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()
