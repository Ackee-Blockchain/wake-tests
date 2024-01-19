import pytest

from wake.testing import *

from .utils import UINT256_MAX
from .suite_abc import ERC20Base


class ERC20Fingerprint(ERC20Base):
    """Tests of level **Fingerprint** check feature properties of the contract;
    these are neither desirable nor undesirable properties but indicate
    implementation choices of the contract.

    Examples of fingerprint properties include the infinite approval property;
    which holds if once the approval is set to `type(uint256).max`, it is not
    decreased by `transferFrom` operations.
    """

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_can_approve_more_than_balance(self):
        """The token ALLOWS tokenApprover to call `approve` of an amount higher than her balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = 100

        # approve with zero balance
        self.assert_approve_valid(account_owner, account_spender, amount)

        # approve with non-zero balance
        self.mint(account_owner, amount)
        self.assert_approve_valid(account_owner, account_spender, amount * 2)

        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_infinite_approval_constant(self):
        """The token HAS infinite approval property. If the approval is set to type(uint256).max and a `transfer` is called, the allowance doesn't decrease."""
        self.static_max_allowance = True
        self.setup_contract()

        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        approve_amount = UINT256_MAX
        mint_amount = 200
        send_amount = 100

        self.mint(account_owner, mint_amount)
        self.assert_approve_valid(account_owner, account_spender, approve_amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_infinite_approval_not_constant(self):
        """The token DOES NOT have infinite approval property. If the approval is set to type(uint256).max and a `transfer` is called, the allowance decreases."""
        self.static_max_allowance = False
        self.setup_contract()

        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        approve_amount = UINT256_MAX
        mint_amount = 200
        send_amount = 100

        self.mint(account_owner, mint_amount)
        self.assert_approve_valid(account_owner, account_spender, approve_amount)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, send_amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_maintains_approval_lower_than_balance(self):
        """TokenApprover MUST maintain at least the said amount in her balance before she can make a `transfer` call to another account."""
        # As far as I understand it, the total allowance of a tokenApprover should always be less than or equal to her balance
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender_1 = default_chain.accounts[1]
        account_spender_2 = default_chain.accounts[2]
        initial_balance = 350
        allowance_1 = 100
        allowance_2 = 200
        send_amount = 100

        # balance: 350, total allowance: 300
        self.mint(account_owner, initial_balance)
        self.assert_approve_valid(account_owner, account_spender_1, allowance_1)
        self.assert_approve_valid(account_owner, account_spender_2, allowance_2)

        # let's try to send 100 to account_spender_1
        # if it reverts, that means that test condition is satisfied
        # if it succeeds, that means the balance can be less than the sum of allowances
        self.assert_transfer_reverts(account_owner, account_spender_1, send_amount)

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_overwrite_approve_positive_to_positive(self):
        """Consecutive calls of `approve` function of positive-to-positive amounts CAN be called."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]

        self.assert_approve_valid(account_owner, account_spender, UINT256_MAX)
        self.assert_approve_valid(account_owner, account_spender, 10)
        self.assert_approve_valid(account_owner, account_spender, 1)

        self.assert_allowances_match_expected()

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_reverts_if_approval_greater_than_balance(self):
        """The token REVERTS if a tokenApprover approves a tokenApprovee more than its balance."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        balance = 100
        allowance = 200

        self.mint(account_owner, balance)
        try:
            self.assert_approve_valid(account_owner, account_spender, allowance)
            approve_reverts = False
        except:
            approve_reverts = True

        assert (
            approve_reverts
        ), "The token must revert if a tokenApprover approves more than its balance."

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_reverts_on_infinite_approval(self):
        """The token REVERTS if one set the approval to type(uint256).max."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = UINT256_MAX

        try:
            self.assert_approve_valid(account_owner, account_spender, amount)
            approve_reverts = False
        except:
            approve_reverts = True

        assert (
            approve_reverts
        ), "The token must revert if one sets the approval to type(uint256).max."

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_transferFrom_decrease_allowance_gt_expected(self):
        """A successful `transferFrom` call of a positive amount DECREASES the allowance of the tokenSender by MORE than the transferred amount."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 300
        allowance = 200
        send_amount = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)

        try:
            # if the token decreases the allowance by more than the transferred amount, this will fail
            self.assert_transferFrom_succeeds(
                account_owner, account_spender, account_receiver, send_amount
            )
            assert (
                False
            ), "The token must decrease the allowance by MORE than the transferred amount."
        except:
            # let's check if the allowance is DECREASED by more than the transferred amount
            allowance_after_erc20 = self.erc20.allowance(account_owner, account_spender)
            allowance_after_mock = self.erc20_mock.allowance(
                account_owner, account_spender
            )
            assert (
                allowance_after_erc20 < allowance
                and allowance_after_erc20 < allowance_after_mock
            ), "The token must DECREASE the allowance by MORE than the transferred amount."

    @default_chain.connect()
    @pytest.mark.xfail(reason="This is not a part of the standard.")
    def test_transferFrom_decrease_allowance_lt_expected(self):
        """A successful `transferFrom` call of a positive amount DECREASES the allowance of the tokenSender by LESS than the transferred amount."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 300
        allowance = 200
        send_amount = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)

        try:
            # if the token decreases the allowance by more than the transferred amount, this will fail
            self.assert_transferFrom_succeeds(
                account_owner, account_spender, account_receiver, send_amount
            )
            assert (
                False
            ), "The token must decrease the allowance by LESS than the transferred amount."
        except:
            # let's check if the allowance is DECREASED by more than the transferred amount
            allowance_after_erc20 = self.erc20.allowance(account_owner, account_spender)
            allowance_after_mock = self.erc20_mock.allowance(
                account_owner, account_spender
            )
            assert (
                allowance > allowance_after_erc20 > allowance_after_mock
            ), "The token must DECREASE the allowance by LESS than the transferred amount."
