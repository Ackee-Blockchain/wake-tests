from wake.testing import *
from wake.testing.fuzzing import *

from .IERC20 import IERC20
from .differential import ERC20DifferentialTest
from .mock import ERC20Mock, Balances, Allowances


class ERC20FuzzTest(FuzzTest):
    def __init__(
        self,
        token: Account,
        initial_supply: uint = 0,
        initial_balances: Balances = None,
        initial_allowances: Allowances = None,
        decimals: uint8 = 18,
        mint_amount: uint = 300,
        static_max_allowance: bool = True,
    ) -> None:
        self.token = token
        self.initial_supply = initial_supply
        self.initial_balances = initial_balances
        self.initial_allowances = initial_allowances
        self.erc20 = IERC20(token.address)
        self.pre_mint = mint_amount * 10**decimals
        self.static_max_allowance = static_max_allowance
        super().__init__()

    def pre_sequence(self) -> None:
        self.erc20_mock = ERC20Mock(
            initial_supply=self.initial_supply,
            initial_balances=self.initial_balances,
            initial_allowances=self.initial_allowances,
            static_max_allowance=self.static_max_allowance,
        )
        self.test_wrapper = ERC20DifferentialTest(self.erc20, self.erc20_mock)

        to = default_chain.default_tx_account
        self.test_wrapper.mint(to, self.pre_mint)
        return super().pre_sequence()

    @flow()
    def flow_approve(self, amount: uint) -> None:
        owner = random_account()
        spender = random_address(zero_address_prob=0.01)
        self.test_wrapper.assert_approve(owner, spender, amount)

    @flow()
    def flow_transfer(self, amount: uint) -> None:
        owner = random_account()
        receiver = random_address(zero_address_prob=0.01)
        self.test_wrapper.assert_transfer(owner, receiver, amount)

    @flow()
    def flow_transferFrom(self, amount: uint) -> None:
        owner = random_address(zero_address_prob=0.01)
        receiver = random_address(zero_address_prob=0.01)
        spender = random_account()
        self.test_wrapper.assert_transferFrom(owner, spender, receiver, amount)
