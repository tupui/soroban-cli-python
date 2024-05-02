import json
import os
import pathlib

import pytest
import soroban
from stellar_sdk import Keypair, scval


class TestIdentity:
    def test_file(self):
        alice_fname = pathlib.Path(__file__).parent / "alice.toml"
        soroban.Identity(_env_file=alice_fname)

    def test_from_pk(self):
        keypair = Keypair.random()
        soroban.Identity(secret_key=keypair.secret)
        soroban.Identity(keypair=keypair)

    def test_from_source_account(self):
        # identity.toml exists
        os.chdir(pathlib.Path(__file__).parent)
        soroban.Identity.from_source_account()
        alice_fname = pathlib.Path(__file__).parent / "alice.toml"
        soroban.Identity.from_source_account(account=alice_fname)

        keypair = Keypair.random()
        soroban.Identity.from_source_account(account=keypair)

        soroban.Identity.from_source_account(account=keypair.secret)

    def test_raises(self):
        os.chdir(pathlib.Path(__file__).parent.parent)
        msg = "Either provide a seed phrase, secret key"
        with pytest.raises(ValueError, match=msg):
            soroban.Identity()

        keypair = Keypair.random()
        with pytest.raises(ValueError, match=msg):
            soroban.Identity(public_key=keypair.public_key)


class TestNetworkConfig:
    def test_from_network(self):
        testnet = pathlib.Path(__file__).parent / "testnet.toml"
        soroban.NetworkConfig.from_network(network=testnet)


class TestParams:
    def test_parameter(self):
        args = {"name": "distributor", "type": "int128", "value": 10}
        soroban.Parameter(**args).model_dump()

        args = {"name": "distributor", "type": "int128", "value": scval.to_int128(10)}
        soroban.Parameter(**args).model_dump()

        args = {
            "name": "thresholds",
            "type": "vec",
            "value": [scval.to_int128(10), {"type": "uint32", "value": 4}],
        }
        soroban.Parameter(**args).model_dump()

        args = {
            "name": "thresholds",
            "type": "vec",
            "value": [
                scval.to_int128(10),
                {"type": "int128", "value": scval.to_int128(10)},
            ],
        }
        soroban.Parameter(**args).model_dump()

    def test_parameters(self):
        fname = pathlib.Path(__file__).parent / "params_invoke.json"
        with open(fname, "rb") as fd:
            args = json.load(fd)
        soroban.Parameters(args=args).model_dump()
