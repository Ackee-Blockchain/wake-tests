from dataclasses import fields
from functools import lru_cache, wraps
from typing import Dict
from wake.testing import Account, Address, uint, keccak256


Allowances = Dict[Address, Dict[Address, uint]]
Balances = Dict[Address, uint]

UINT256_MAX = 2**256 - 1


# Warnings


class ZeroAddressWarning(Warning):
    ...


class NoExplicitApprovalWarning(Warning):
    ...


class IncorrectReturnValueWarning(Warning):
    ...


class ReturnInsteadOfRevertWarning(Warning):
    ...


# Helpers


@lru_cache(maxsize=32)
def keccak256_hash(_string: str) -> bytes:
    return keccak256(bytes(_string, encoding="utf8"))


@lru_cache(maxsize=32)
def selector(_fn_signature: str) -> bytes:
    return keccak256_hash(_fn_signature)[:4]


def shorten_address(address: Address) -> str:
    return f"{address[:5]}..{address[-3:]}"


def all_events_emitted(tx_events, expected_events) -> bool:
    # Different implementations have different argument namings of events
    # The things that should be the same are:
    # 1. Event name
    # 2. Arguments values
    # 3. Arguments order
    def _cvt_event(_event):
        # Events are dataclasses
        values = []
        for f in fields(_event):
            if f.name == "origin":
                # a new field in version 4.0.0
                continue
            value = getattr(_event, f.name)
            # cannot directly compare Address and Account instances
            value = value.address if isinstance(value, Account) else value
            values.append(value)
        return _event.__class__.__name__, *values

    tx_events = [_cvt_event(e) for e in tx_events]
    expected_events = [_cvt_event(e) for e in expected_events]
    for event in expected_events:
        if event not in tx_events:
            return False
    return True


# Wrappers


# source: https://stackoverflow.com/questions/25828864/catch-before-after-function-call-events-for-all-functions-in-class
def decorate_all_functions(function_decorator):
    def decorator(cls):
        for name, obj in vars(cls).items():
            if callable(obj):
                try:
                    obj = obj.__func__  # unwrap Python 2 unbound method
                except AttributeError:
                    pass  # not needed in Python 3
                setattr(cls, name, function_decorator(obj))
        return cls

    return decorator


def account_to_address_converter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cvt_args = []
        for arg in args:
            # not using isinstance to not overwrite contracts instances
            if type(arg) is Account:
                arg = arg.address
            cvt_args.append(arg)
        cvt_kwargs = {}
        for name, value in kwargs.items():
            # not using isinstance to not overwrite contracts instances
            if type(value) is Account:
                value = value.address
            cvt_kwargs[name] = value
        res = func(*cvt_args, **cvt_kwargs)
        return res

    return wrapper
