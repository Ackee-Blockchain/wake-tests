# ERC Tests for Wake

![horizontal splitter](https://github.com/Ackee-Blockchain/wake-detect-action/assets/56036748/ec488c85-2f7f-4433-ae58-3d50698a47de)

This Python package implements ready-to-use Python tests for the most common ERC standards. See the list of implemented tests below.

## Dependencies

- Python (version 3.8 or higher)
- Wake (version 4.0.0 or higher)

## Installation

The installation is simple. Just run the following command:

```bash
pip install wake_tests
```

This will also install `eth-wake` in case you don't have it installed already.

## Test Suites

Test suites implement two types of tests: **unit tests** and **fuzz tests**. Unit tests are used to test individual functions and methods. Fuzz tests are used to test functions with random inputs. Fuzz tests are useful for finding bugs in functions that are not covered by unit tests.

### ERC-20 

ERC-20 tests are fully implemented. Test suites are inspired by [Runtime Verification's ERC-20 tests](https://ercx.runtimeverification.com/whats-being-tested?standard=erc-20). A comprehensive example of how to use the test suite as well as the comprehensive documentation can be found in [examples/erc20](/examples/erc20/).

### Other Standards

More standards (ERC-721, ERC-1155, etc.) are coming soon.
