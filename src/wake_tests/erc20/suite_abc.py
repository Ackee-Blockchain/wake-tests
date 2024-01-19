import abc
from collections import defaultdict
from typing import Dict, Union

from wake.testing import *

from .IERC20 import IERC20
from .mock import ERC20Mock
from .utils import Allowances
from .differential import ERC20DifferentialTest


class ERC20Base(abc.ABC):
    decimals: int = 18
    initial_supply: int = 0
    initial_balances: Dict[Union[Account, Address], uint] = {}
    static_max_allowance: bool = True

    @classmethod
    @abc.abstractmethod
    def deploy_token(cls) -> Account:
        ...

    def setup_contract(self):
        self.token = self.deploy_token()
        self.erc20 = IERC20(self.token.address)
        self.erc20_mock = ERC20Mock(
            initial_supply=self.initial_supply,
            initial_balances=self.initial_balances,
            initial_allowances=self._init_allowances(),
            static_max_allowance=self.static_max_allowance,
        )
        self.differential = ERC20DifferentialTest(self.erc20, self.erc20_mock)

    def assert_total_supply_matches_expected(self) -> None:
        self.differential.assert_total_supply_matches_expected()

    def assert_approve_valid(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
    ) -> None:
        self.differential.assert_approve_valid(owner, spender, amount)

    def assert_approve_zero_spender_valid(
        self,
        owner: Union[Account, Address],
        amount: uint,
        should_zero_spender_fail: bool = False,
    ) -> None:
        self.differential.assert_approve_zero_spender_valid(
            owner, amount, should_zero_spender_fail=should_zero_spender_fail
        )

    def assert_transfer_succeeds(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self.differential.assert_transfer_succeeds(owner, receiver, amount)

    def assert_transfer_reverts(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self.differential.assert_transfer_reverts(owner, receiver, amount)

    def assert_transferFrom_succeeds(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self.differential.assert_transferFrom_succeeds(owner, spender, receiver, amount)

    def assert_transferFrom_reverts(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
    ) -> None:
        self.differential.assert_transferFrom_reverts(owner, spender, receiver, amount)

    def assert_balances_match_expected(self) -> None:
        self.differential.assert_balances_match_expected()

    def assert_allowances_match_expected(self) -> None:
        self.differential.assert_allowances_match_expected()

    def mint(self, to: Address, amount: uint) -> None:
        self.differential.mint(to, amount)

    def _init_allowances(self) -> Allowances:
        allowances = defaultdict(lambda: defaultdict(uint))
        for owner in default_chain.accounts:
            for spender in default_chain.accounts:
                allowances[owner.address][spender.address] = self.erc20.allowance(
                    owner, spender
                )
        return allowances
