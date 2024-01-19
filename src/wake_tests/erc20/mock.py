from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Union

from wake.testing import *

from .IERC20 import IERC20
from .utils import (
    Allowances,
    Balances,
    UINT256_MAX,
    account_to_address_converter,
    decorate_all_functions,
)


Events = List[Any]


@decorate_all_functions(account_to_address_converter)
class ERC20Mock:
    def __init__(
        self,
        initial_supply: uint = 0,
        initial_balances: Dict[Union[Account, Address], uint] = None,
        initial_allowances: Dict[
            Union[Account, Address], Dict[Union[Account, Address], uint]
        ] = None,
        static_max_allowance: bool = True,
    ) -> None:
        self.total_supply = initial_supply
        self.balances: Balances = defaultdict(uint)
        self.allowances: Allowances = defaultdict(lambda: defaultdict(uint))
        self.static_max_allowance = static_max_allowance

        # copy with convert Account -> Address
        for account, value in (initial_balances or {}).items():
            address = account.address if type(account) is Account else account
            self.balances[address] = value

        for owner, allowances in (initial_allowances or {}).items():
            owner_address = owner.address if type(owner) is Account else owner
            for spender, value in allowances.items():
                spender_address = (
                    spender.address if type(spender) is Account else spender
                )
                self.allowances[owner_address][spender_address] = value

        assert self.total_supply >= sum(
            self.balances.values()
        ), "The initial supply must not be less than the sum of the initial balances"

    def balanceOf(self, account: Union[Account, Address]) -> uint:
        return self.balances[account]

    def allowance(
        self, owner: Union[Account, Address], spender: Union[Account, Address]
    ) -> uint:
        return self.allowances[owner][spender]

    def mint(
        self,
        to: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
    ) -> Events:
        assert allow_zero_account or to != Address.ZERO

        self.balances[to] += amount
        self.total_supply += amount
        return [IERC20.Transfer(Address.ZERO, to, amount)]

    def burn(
        self,
        from_: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
    ) -> Events:
        assert allow_zero_account or from_ != Address.ZERO
        assert self.balances[from_] >= amount

        self.balances[from_] -= amount
        self.total_supply -= amount
        return [IERC20.Transfer(from_, Address.ZERO, amount)]

    def approve(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
        dry_run: bool = False,
    ) -> Events:
        # we cannot approve from 0x0
        assert owner != Address.ZERO
        assert allow_zero_account or spender != Address.ZERO

        if not dry_run:
            self.allowances[owner][spender] = amount
        return [IERC20.Approval(owner, spender, amount)]

    def transfer(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
        dry_run: bool = False,
    ) -> Events:
        # we cannot transfer from 0x0 (however, 0 value MAY allow it)
        assert amount == 0 or owner != Address.ZERO
        assert allow_zero_account or receiver != Address.ZERO
        assert self.balances[owner] >= amount

        if not dry_run:
            self.balances[owner] -= amount
            self.balances[receiver] += amount
        return [IERC20.Transfer(owner, receiver, amount)]

    def transferFrom(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
        dry_run: bool = False,
    ) -> Events:
        # 0x0 cannot perform any operation
        assert spender != Address.ZERO
        assert self.allowances[owner][spender] >= amount
        # transfer() also checks other parameters

        self.transfer(
            owner,
            receiver,
            amount,
            allow_zero_account=allow_zero_account,
            dry_run=dry_run,
        )
        if not dry_run:
            if (
                self.allowances[owner][spender] != UINT256_MAX
                or not self.static_max_allowance
            ):
                self.allowances[owner][spender] -= amount
        return [IERC20.Transfer(owner, receiver, amount)]

    def should_transfer_succeed(
        self,
        owner: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
    ) -> bool:
        try:
            self.transfer(
                owner,
                receiver,
                amount,
                allow_zero_account=allow_zero_account,
                dry_run=True,
            )
        except AssertionError:
            return False
        else:
            return True

    def should_approve_succeed(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
    ) -> bool:
        try:
            self.approve(
                owner=owner,
                spender=spender,
                amount=amount,
                allow_zero_account=allow_zero_account,
                dry_run=True,
            )
        except AssertionError:
            return False
        else:
            return True

    def should_transferFrom_succeed(
        self,
        owner: Union[Account, Address],
        spender: Union[Account, Address],
        receiver: Union[Account, Address],
        amount: uint,
        *,
        allow_zero_account: bool = False,
    ) -> bool:
        try:
            self.transferFrom(
                owner,
                spender,
                receiver,
                amount,
                allow_zero_account=allow_zero_account,
                dry_run=True,
            )
        except AssertionError:
            return False
        else:
            return True
