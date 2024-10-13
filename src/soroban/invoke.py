import logging
import time

import stellar_sdk
from stellar_sdk import xdr
from stellar_sdk.exceptions import PrepareTransactionException, SdkError
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus

import soroban.models as soroban_models

__all__ = ["invoke"]


logger = logging.getLogger(__name__)


def invoke(
    contract_id: str,
    function_name: str,
    args: soroban_models.Parameters | list[xdr.SCVal] | None = None,
    *,
    source_account: soroban_models.Identity | stellar_sdk.Keypair | str | None = None,
    network: soroban_models.NetworkConfig | soroban_models.NetworkConfig | None = None,
) -> xdr.SCVal:
    """Invoke a Soroban contract.

    Parameters
    ----------
    contract_id : contract hash.
    function_name : name of the function to invoke.
    args : parameters passed to the contract function.
    source_account : signing account.
    network : network to use.

    Returns
    -------
    result : return value of the contract invocation.

    """
    identity = (
        source_account
        if isinstance(source_account, soroban_models.Identity)
        else soroban_models.Identity.from_source_account(account=source_account)
    )
    network = (
        network
        if isinstance(network, soroban_models.NetworkConfig)
        else soroban_models.NetworkConfig.from_network(network=network)
    )
    args = args.model_dump() if isinstance(args, soroban_models.Parameters) else args

    soroban_server = stellar_sdk.SorobanServer(network.rpc_url)
    source_account_ = soroban_server.load_account(identity.public_key)

    tx = (
        stellar_sdk.TransactionBuilder(
            source_account_, network.network_passphrase, base_fee=network.base_fee
        )
        .add_time_bounds(0, 0)
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name=function_name,
            parameters=args,
        )
        .build()
    )

    try:
        tx = soroban_server.prepare_transaction(tx)
    except PrepareTransactionException as err:
        err_msg = err.simulate_transaction_response.error
        raise SdkError(
            f"Failed to simulate transaction: {err_msg}\nXDR:\n{tx.to_xdr()}\nEnveloppe:\n{tx.transaction}"
        )

    tx.sign(identity.keypair)
    transaction = soroban_server.send_transaction(tx)

    if transaction.status != SendTransactionStatus.PENDING:
        raise SdkError(f"Failed to send transaction: {transaction.hash}")

    i = 0
    while i < 10:
        transaction_result = soroban_server.get_transaction(transaction.hash)
        if transaction_result.status != GetTransactionStatus.NOT_FOUND:
            break
        time.sleep(3)
        i += 1
    else:
        raise SdkError(f"Timeout - could not validate transaction: {transaction.hash}")

    transaction_envelope = stellar_sdk.parse_transaction_envelope_from_xdr(
        transaction_result.envelope_xdr, network_passphrase=network.network_passphrase
    )
    logger.debug(transaction_envelope)

    if transaction_result.status == GetTransactionStatus.SUCCESS:
        transaction_meta = xdr.TransactionMeta.from_xdr(
            transaction_result.result_meta_xdr
        )
        result = transaction_meta.v3.soroban_meta.return_value
        return result
    else:
        raise SdkError(f"Transaction failed: {transaction_result.result_xdr}")
