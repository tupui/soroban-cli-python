from decimal import Decimal

import pytest

import soroban


@pytest.mark.skip
def test_create_account():
    source_account = "SDEUQZ7PMHT7VDP3TYZMBKUVES3W6CTXT5L2ZR5NROWQJIDE4QFUXW6Q"

    soroban.create_account(name="bob", source_account=source_account)


@pytest.mark.skip
def test_create_asset():
    source_account = "SDEUQZ7PMHT7VDP3TYZMBKUVES3W6CTXT5L2ZR5NROWQJIDE4QFUXW6Q"

    soroban.create_asset(name="BOBI", mint=Decimal(10), source_account=source_account)
