# ERC-20 Tests for Wake (Usage Example)

This is an example NPM project with several contracts that implement ERC-20 standards using popular frameworks. To run the examples, do the following:

```bash
npm install
wake init
wake test
```

## Using the Tests in Your Project

To use the test suite, you first need to generate [`pytypes`](https://ackeeblockchain.com/wake/docs/latest/testing-framework/getting-started/#generating-pytypes) for your contract:

```bash
cd <your-project-dir>
wake init pytypes
```

### Unit Tests

This will generate `pytypes` for all Solidity files and also create the `tests/test_default.py` script. You need to define how your token is deployed and set up class variables there.

Let's assume that you have a `Token` contract defined in `/contracts/Token.sol` that implements the ERC-20 standard. Your `tests/test_default.py` will therefore look like this:

```python
from wake.testing import *
# test suites are described below
from wake_tests.erc20 import (
    ERC20Abi,
    ERC20Minimal,
    ERC20Recommended,
    ERC20Desirable,
    ERC20Fingerprint,
)

# pytypes generated for your contract
from pytypes.contracts.Token import Token


class TestToken(
    ERC20Abi,
    ERC20Minimal,
    ERC20Recommended,
    ERC20Desirable,
    ERC20Fingerprint
):
    # decimals for the token, default is 18
    decimals = 18
    # how much supply is in the beginning, default is 0
    initial_supply = 0
    # A dictionary of addresses and their initial balances, default is {}
    initial_balances = {}
    # If >0, Wake will try to pre-mint this amount automatically by using its
    # heuristics, but if it fails, you can set it to 0 and mint the tokens
    # manually in the `deploy_token` method. Note that the `initial_supply`
    # should be equal to the sum of `initial_balances` and also equal to
    # `mint_amount`
    mint_amount = 0
    # Defines the behavior of the allowance after calling `transferFrom` when
    # the allowance is set to 2**256-1. If True, the allowance is not expected
    # to change, if False, the allowance is expected to be decreased by the
    # transferred amount.
    static_max_allowance = True

    @classmethod
    def deploy_token(cls) -> Account:
        """Override this method and provide instructions on how to deploy
        your token. If you choose to set `mint_amount` to 0 but still want
        to pre-mint tokens, you can do it here, too.
        """
        owner = default_chain.accounts[0]
        default_chain.set_default_accounts(owner)
        token = cls._token_class.deploy(cls.initial_supply)
        return token
```

Now, you can run the tests:

```bash
wake test
```

### Fuzz Tests

The principle is the same as with unit tests. You need to define how your token is deployed and run a special function from the `ERC20FuzzTest` class. This function takes several parameters similar to the class variables in the unit tests. Additionally, you need to specify how many sequences (independent runs) and [flows](https://ackeeblockchain.com/wake/docs/latest/testing-framework/fuzzing/#flows) you want to run.

```python
from wake.testing import *
from wake_tests.erc20 import ERC20FuzzTest

# pytypes generated for your contract
from pytypes.contracts.Token import Token


# the number of independent runs
SEQUENCES = 10
# the number of flows per run
FLOWS = 50


@default_chain.connect(accounts=20)
def test_token_fuzz():
    # deploy as before
    owner = default_chain.accounts[0]
    default_chain.set_default_accounts(owner)
    token = token_class.deploy(0)

    # run the fuzz test; arguments are the same as the class variables
    # in the unit tests
    ERC20FuzzTest(
        token,
        initial_supply=0,
        initial_balances=None,
        initial_allowances=None,
        decimals=18,
        mint_amount=300,
        static_max_allowance=True,
    ).run(SEQUENCES, FLOWS)
```

Now, you can run the tests:

```bash
wake test
```

## Unit Test Suites

Descriptions are taken from [Runtime Verification's ERC-20 tests](https://ercx.runtimeverification.com/whats-being-tested?standard=erc-20).

- `ERC20Abi`: Tests of level ABI check the name, inputs, and outputs of the token functions.
- `ERC20Minimal`: Tests of level Minimal check the properties that MUST be respected.
- `ERC20Recommended`: Tests of level Recommended check the properties that SHOULD be respected.
- `ERC20Desirable`: Tests of level Desirable check properties we deem important to the sane functioning of a token and complement the standard specification.
- `ERC20Fingerprint`: Tests of level Fingerprint check feature properties of the contract; these are neither desirable nor undesirable properties but indicate implementation choices of the contract.
