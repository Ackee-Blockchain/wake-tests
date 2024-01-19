from wake.testing import *
from wake_tests.erc20 import ERC20Abi, ERC20Minimal, ERC20Recommended, ERC20Desirable, ERC20Fingerprint

from pytypes.contracts.BoringERC20 import BoringERC20
from pytypes.contracts.OZERC20 import OZERC20
from pytypes.contracts.PureERC20 import ERC20 as PureERC20
from pytypes.contracts.SoladyERC20 import SoladyERC20
from pytypes.contracts.SolmateERC20 import SolmateERC20


class Base(ERC20Abi, ERC20Minimal, ERC20Recommended, ERC20Desirable, ERC20Fingerprint):
    _token_class = None

    decimals = 18
    initial_supply = 0
    initial_balances = {}
    mint_amount = 0
    static_max_allowance = True

    @classmethod
    def deploy_token(cls) -> Account:
        owner = default_chain.accounts[0]
        default_chain.set_default_accounts(owner)
        token = cls._token_class.deploy(cls.initial_supply)
        return token


class TestBoringERC20(Base):
    _token_class = BoringERC20


class TestOZERC20(Base):
    _token_class = OZERC20


class TestPureERC20(Base):
    _token_class = PureERC20


class TestSoladyERC20(Base):
    _token_class = SoladyERC20


class TestSolmateERC20(Base):
    _token_class = SolmateERC20
