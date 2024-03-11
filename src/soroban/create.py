import logging
from decimal import Decimal

import stellar_sdk
from stellar_sdk.exceptions import SdkError
import tomli_w

import soroban.models as soroban_models


__all__ = ["create_account", "create_asset"]


logger = logging.getLogger(__name__)


def create_account(
    *,
    name: str,
    balance: Decimal = Decimal(10),
    source_account: soroban_models.Identity | stellar_sdk.Keypair | str | None = None,
    network: soroban_models.NetworkConfig | soroban_models.NetworkConfig | None = None,
) -> stellar_sdk.Keypair:
    """Create an account.

    It automatically stores the secret key to a file.

    Parameters
    ----------
    name : name of the account. Used to name the toml file.
    balance : initial balance to transfer to the account from the source.
    source_account : account creating the new account.
    network : network to use.

    Returns
    -------
    account : the new account.

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

    horizon_server = stellar_sdk.Server(network.horizon_url)
    source_account_ = horizon_server.load_account(identity.public_key)

    # the new account itself
    new_account = stellar_sdk.Keypair.random()
    with open(f"{name}.toml", "wb") as fd:
        tomli_w.dump({"secret_key": new_account.secret}, fd)

    tx = (
        stellar_sdk.TransactionBuilder(
            source_account=source_account_,
            network_passphrase=network.network_passphrase,
            base_fee=network.base_fee,
        )
        .append_create_account_op(
            destination=new_account.public_key, starting_balance=str(balance)
        )
        .set_timeout(30)
        .build()
    )
    tx.sign(identity.keypair)
    response = horizon_server.submit_transaction(tx)
    if not response["successful"]:
        raise SdkError(response)
    logger.debug(f"Create account Op Resp:\n{response}")
    return new_account


def create_asset(
    *,
    name: str,
    mint: Decimal = Decimal(1e9),
    source_account: soroban_models.Identity | stellar_sdk.Keypair | str | None = None,
    network: soroban_models.NetworkConfig | soroban_models.NetworkConfig | None = None,
) -> None:
    """Create a Stellar Asset.

    It creates two accounts:

    1. Issuer account: create the asset
    2. Distribution account: set a trustline to the asset and use to manage the
       asset.

    Parameters
    ----------
    name : The asset code, in the formats specified in Stellar's guide on assets.
    mint : Initial
    source_account : Account used to create the issuer and distribution accounts.
    network : network to use.

    """
    network = (
        network
        if isinstance(network, soroban_models.NetworkConfig)
        else soroban_models.NetworkConfig.from_network(network=network)
    )

    issuer = create_account(name="issuer", source_account=source_account)
    distributor = create_account(name="distributor", source_account=source_account)

    # Transactions require a valid sequence number that is specific to this account.
    # We can fetch the current sequence number for the source account from Horizon.
    horizon_server = stellar_sdk.Server(network.horizon_url)
    distributor_account = horizon_server.load_account(distributor.public_key)

    asset = stellar_sdk.Asset(code=name, issuer=issuer.public_key)

    # Establish a trust line between distribution account and the asset
    trust_transaction = (
        stellar_sdk.TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=network.network_passphrase,
            base_fee=network.base_fee,
        )
        .append_change_trust_op(asset=asset)
        .set_timeout(30)
        .build()
    )

    trust_transaction.sign(distributor)
    response = horizon_server.submit_transaction(trust_transaction)
    if not response["successful"]:
        raise SdkError(response)
    logger.debug(f"Change Trust Op Resp:\n{response}")

    issuer_account = horizon_server.load_account(issuer.public_key)
    # Second, the issuing account actually sends a payment using the asset.
    payment_transaction = (
        stellar_sdk.TransactionBuilder(
            source_account=issuer_account,
            network_passphrase=network.network_passphrase,
            base_fee=network.base_fee,
        )
        .append_payment_op(destination=distributor.public_key, amount=mint, asset=asset)
        .set_timeout(30)
        .build()
    )
    payment_transaction.sign(issuer)
    response = horizon_server.submit_transaction(payment_transaction)
    if not response["successful"]:
        raise SdkError(response)
    logger.debug(f"Payment Op Resp:\n{response}")
