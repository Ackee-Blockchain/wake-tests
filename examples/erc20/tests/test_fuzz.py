from wake.testing import *
from wake_tests.erc20 import ERC20FuzzTest

from pytypes.contracts.BoringERC20 import BoringERC20
from pytypes.contracts.OZERC20 import OZERC20
from pytypes.contracts.PureERC20 import ERC20 as PureERC20
from pytypes.contracts.SoladyERC20 import SoladyERC20
from pytypes.contracts.SolmateERC20 import SolmateERC20


SEQUENCES = 10
FLOWS = 50


def _deploy_erc20(token_class) -> Account:
    owner = default_chain.accounts[0]
    default_chain.set_default_accounts(owner)
    token = token_class.deploy(0)
    return token


@default_chain.connect(accounts=20)
def test_boring_fuzz():
    token = _deploy_erc20(BoringERC20)
    ERC20FuzzTest(
        token,
        initial_supply=0,
        initial_balances=None,
        initial_allowances=None,
        decimals=18,
        mint_amount=300,
        static_max_allowance=True,
    ).run(SEQUENCES, FLOWS)


@default_chain.connect(accounts=20)
def test_oz_fuzz():
    token = _deploy_erc20(OZERC20)
    ERC20FuzzTest(token).run(SEQUENCES, FLOWS)


@default_chain.connect(accounts=20)
def test_pure_fuzz():
    token = _deploy_erc20(PureERC20)
    ERC20FuzzTest(token).run(SEQUENCES, FLOWS)


@default_chain.connect(accounts=20)
def test_solady_fuzz():
    token = _deploy_erc20(SoladyERC20)
    ERC20FuzzTest(token).run(SEQUENCES, FLOWS)


@default_chain.connect(accounts=20)
def test_solmate_fuzz():
    token = _deploy_erc20(SolmateERC20)
    ERC20FuzzTest(token).run(SEQUENCES, FLOWS)
