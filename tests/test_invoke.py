import pytest

import soroban


@pytest.mark.skip
def test_invoke():
    contract_id = "CC22IAGPHR4DXI73WSI4L65TTB3F5A2DF7FP5PPNIOLVX5NQWSVR4TID"
    source_account = "SDEUQZ7PMHT7VDP3TYZMBKUVES3W6CTXT5L2ZR5NROWQJIDE4QFUXW6Q"

    soroban.invoke(
        contract_id=contract_id, function_name="version", source_account=source_account
    )
