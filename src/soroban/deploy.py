"""
def deploy_asset(*, asset: Asset, source_account: Keypair) -> None:
    source_account_ = server.load_account(source_account.public_key)
    tx = (
        TransactionBuilder(source_account_, Network.TESTNET_NETWORK_PASSPHRASE)
        .set_timeout(300)
        .append_create_stellar_asset_contract_from_asset_op(asset=asset)
        .build()
    )
    # tx = soroban_server.prepare_transaction(tx)
    # tx.sign(kp)
    # send_transaction_data = soroban_server.send_transaction(tx)
    # if get_transaction_data.status == GetTransactionStatus.SUCCESS:
    #     transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
    #         get_transaction_data.result_meta_xdr
    #     )
    #     result = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hash  # type: ignore
    #     contract_id = StrKey.encode_contract(result)
    #     print(f"contract id: {contract_id}")
"""
