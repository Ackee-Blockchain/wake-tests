from wake.testing import *

from .suite_abc import ERC20Base


class ERC20Minimal(ERC20Base):
    """Tests of level **Minimal** check the properties that MUST be respected."""

    @default_chain.connect()
    def test_positive_approval_event_emission(self):
        """A successful `approve` call of positive amount MUST emit the `Approval` event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = 100

        # events are validated inside
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_approve_allows_positive_transferFrom(self):
        """After a tokenApprover approves a tokenApprovee some positive amount via an `approve` call, any positive amount up to the said amount MUST be transferable by tokenApprovee via a `transferFrom` call, provided a sufficient balance of tokenApprover."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        balance = 200
        allowance = 100
        amount_1 = 50
        amount_2 = 75

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_spender, amount_1
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_spender, amount_1
        )
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_spender, amount_1
        )

        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_spender, amount_2
        )
        self.assert_transferFrom_reverts(
            account_owner, account_spender, account_spender, amount_2
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_approve_allows_zero_transferFrom(self):
        """After a tokenApprover approves a tokenApprovee some positive amount via an `approve` call, zero amount MUST be transferable by tokenApprovee via a `transferFrom` call, provided a sufficient balance of tokenApprover."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_spender, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_approve_leads_to_allowance(self):
        """Positive approved amount MUST be reflected in the allowance correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = 100

        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_transfer_event_emission(self):
        """A successful `transfer` call of positive amount MUST emit the Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]
        amount = 100

        self.mint(account_owner, amount)
        # events are validated inside
        self.assert_transfer_succeeds(account_owner, account_receiver, amount)

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_positive_transferFrom_event_emission(self):
        """A successful `transferFrom` call of positive amount MUST emit Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        balance = 200
        allowance = 100
        amount = 50

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        # events are validated inside
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, amount
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_user_balance_initialized(self):
        """A successful `balanceOf(account)` call MUST return balance of `account` correctly after two dummy users' balances are initialized."""
        self.setup_contract()
        account_reference = default_chain.accounts[0]
        account_owner = default_chain.accounts[1]
        account_receiver_1 = default_chain.accounts[2]
        account_receiver_2 = default_chain.accounts[3]
        balance = 100
        amount = 50

        self.mint(account_reference, balance)
        self.mint(account_owner, balance)
        self.assert_transfer_succeeds(account_owner, account_receiver_1, amount)
        self.assert_transfer_succeeds(account_owner, account_receiver_2, amount)

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_approval_event_emission(self):
        """A successful `approve` call of zero amount MUST emit the `Approval` event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        amount = 0

        # events are validated inside
        self.assert_approve_valid(account_owner, account_spender, amount)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_approve_leads_to_allowance(self):
        """Zero approved amount MUST be reflected in the allowance correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        initial_allowance = 100

        self.assert_approve_valid(account_owner, account_spender, initial_allowance)
        self.assert_approve_valid(account_owner, account_spender, 0)
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_other_emits_event(self):
        """A successful `transferFrom` of zero amount by any user other than the tokenSender MUST emit a Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        account_other = default_chain.accounts[3]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)

        # events are validated inside
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_other, account_receiver, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_other_possible(self):
        """A successful `transferFrom` call of zero amount by any user other than the tokenSender MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_receiver = default_chain.accounts[2]
        account_other = default_chain.accounts[3]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_receiver, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_other, account_receiver, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_other_to_self_possible(self):
        """A successful `transferFrom` call of zero amount by any user other than the tokenSender to the tokenSender MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_other = default_chain.accounts[2]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_spender, account_owner, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_other, account_owner, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_self_emits_event(self):
        """A successful `transferFrom` call of zero amount by the tokenSender herself MUST emit a Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_other = default_chain.accounts[2]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_spender, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_other, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_self_possible(self):
        """A successful `transferFrom` call of zero amount by the tokenSender herself MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_spender = default_chain.accounts[1]
        account_other = default_chain.accounts[2]
        balance = 200
        allowance = 100

        self.mint(account_owner, balance)
        self.assert_approve_valid(account_owner, account_spender, allowance)
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_spender, 0
        )
        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_other, 0
        )

        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transferFrom_by_self_to_self_possible(self):
        """A successful `transferFrom` call of zero amount by the tokenSender herself to herself MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        self.assert_transferFrom_succeeds(
            account_owner, account_owner, account_owner, 0
        )
        self.assert_balances_match_expected()
        self.assert_allowances_match_expected()

    @default_chain.connect()
    def test_zero_transfer_to_others_emits_event(self):
        """A successful `transfer` call of zero amount to another account MUST emit the Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]

        # events are validated inside
        self.assert_transfer_succeeds(account_owner, account_receiver, 0)
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_zero_transfer_to_others_possible(self):
        """A successful `transfer` call of zero amount to another account MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]
        account_receiver = default_chain.accounts[1]

        # events are validated inside
        self.assert_transfer_succeeds(account_owner, account_receiver, 0)
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_zero_transfer_to_self_emits_event(self):
        """A successful `transfer` call of zero amount to self MUST emit the Transfer event correctly."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        # events are validated inside
        self.assert_transfer_succeeds(account_owner, account_owner, 0)
        self.assert_balances_match_expected()

    @default_chain.connect()
    def test_zero_transfer_to_self_possible(self):
        """A successful `transfer` call of zero amount to self MUST be possible."""
        self.setup_contract()
        account_owner = default_chain.accounts[0]

        # events are validated inside
        self.assert_transfer_succeeds(account_owner, account_owner, 0)
        self.assert_balances_match_expected()
