import pathlib

import pytest
import soroban
from stellar_sdk import Keypair


class TestIdentity:

    def test_file(self):
        alice_fname = pathlib.Path(__file__).parent / "alice.toml"
        soroban.Identity(_env_file=alice_fname)

    def test_from_pk(self):
        keypair = Keypair.random()
        soroban.Identity(secret_key=keypair.secret)
        soroban.Identity(keypair=keypair)

    def test_from_source_account(self):
        alice_fname = pathlib.Path(__file__).parent / "alice.toml"
        soroban.Identity.from_source_account(account=alice_fname)

        keypair = Keypair.random()
        soroban.Identity.from_source_account(account=keypair)

    def test_raises(self):
        with pytest.raises(ValueError, match="provide a secret key or a Keypair"):
            soroban.Identity()

        keypair = Keypair.random()
        with pytest.raises(ValueError, match="provide a secret key or a Keypair"):
            soroban.Identity(public_key=keypair.public_key)


class TestNetworkConfig:

    def test_from_network(self):
        testnet = pathlib.Path(__file__).parent / "testnet.toml"
        soroban.NetworkConfig.from_network(network=testnet)
