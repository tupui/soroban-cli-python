import time

import stellar_sdk
from stellar_sdk import xdr
from stellar_sdk.exceptions import SdkError
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus

import soroban.models as soroban_models

__all__ = ["invoke"]


def invoke(
    contract_id: str,
    function_name: str,
    args: list[xdr.SCVal] | None = None,
    *,
    source_account: stellar_sdk.Keypair | str | None = None,
    network: soroban_models.NetworkConfig | None = None,
):
    identity = soroban_models.Identity.from_source_account(account=source_account)
    network = soroban_models.NetworkConfig() if network is None else network

    soroban_server = stellar_sdk.SorobanServer(network.rpc_url)
    source_account = soroban_server.load_account(identity.public_key)

    tx = (
        stellar_sdk.TransactionBuilder(
            source_account, network.network_passphrase, base_fee=network.base_fee
        )
        .add_time_bounds(0, 0)
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name=function_name,
            parameters=args,
        )
        .build()
    )
    tx = soroban_server.prepare_transaction(tx)
    tx.sign(identity.keypair)
    transaction = soroban_server.send_transaction(tx)

    if transaction.status != SendTransactionStatus.PENDING:
        raise SdkError("Failed to send transaction")

    i = 0
    while i < 10:
        transaction_result = soroban_server.get_transaction(transaction.hash)
        if transaction_result.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
        i += 1
    else:
        raise SdkError("Timeout: could not validate transaction")

    if transaction_result.status == GetTransactionStatus.SUCCESS:
        transaction_meta = xdr.TransactionMeta.from_xdr(
            transaction_result.result_meta_xdr
        )
        if transaction_meta.v3.soroban_meta.return_value.type == xdr.SCValType.SCV_VOID:
            return transaction_meta
    else:
        raise SdkError(f"Transaction failed: {transaction_result.result_xdr}")
