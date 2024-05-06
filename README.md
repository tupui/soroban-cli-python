# API and CLI for Soroban contracts in Python

This package provide tools to interact with Soroban contracts in Python. The
goal is to provide a simple feature set while not depending on the Rust SDK.
This can be useful in environment where Rust and the SDK might be more
difficult to get working (like a Raspberry Pi).

## Getting started

```
pip install soroban
```

This provides a simple way to call contracts without needing to install the
Rust SDK and is a higher level interface compared to using the Python SDK.

```python
import soroban

soroban.invoke(contract_id="AAAA...", function_name="increment")
```

Identity and Network configurations are automatically pulled from the
local configuration or the current working directory. See bellow.

It also provides a CLI
```shell
soroban invoke C... version --source-account=...
```

## Usage

The main feature is to be able to call a Soroban contract function: `soroban.invoke`.

```python
import soroban

soroban.invoke(contract_id="AAAA...", function_name="increment")
```

It also supports passing arguments as a list of `stellar_sdk.SCVal`. This list
can be easily generated

```python
import json
import soroban

args = json.load(...)
args = soroban.Parameters(args=args)
soroban.invoke(contract_id="AAAA...", function_name="init", args=args)
```

The following JSON syntax is supported. Note that vectors are also supported:
```json
[
  {
    "name": "issuer",
    "type": "address",
    "value": "C..."
  },
  {
    "name": "distributor",
    "type": "int128",
    "value": 10
  },
  {
    "name": "claimants",
    "type": "vec",
    "value": [
      {
        "type": "uint32",
        "value": 12
      },
      {
        "type": "int64",
        "value": 20
      }
    ]
  }
]
```

A few helper functions are also provided:

- `soroban.create_account`: create and fund an account from a source account;
- `soroban.create_asset`: create an asset using the classical issuer/distributor model.

## Configuration

The source account and the network to use are set by instantiating `soroban.Identity`
and `soroban.NetworkConfig`, respectively:

```python
import soroban

identity = soroban.Identity()
network = soroban.NetworkConfig()
```

In both cases, the configuration can be set by either adjusting init arguments,
setting up environment variables or using configuration files in toml.

The default path for `soroban.Identity` is `identity.toml` and for `soroban.NetworkConfig` it
is `testnet.toml`. Here are examples of these files:

```toml
secret_key = "S..."
```

```toml
horizon_url = "https://horizon-testnet.stellar.org"
rpc_url = "https://soroban-testnet.stellar.org"
network_passphrase = "Test SDF Network ; September 2015"
```

Any of these fields can be set as an environment variable.

## Acknowledgements

This repository has no affiliation with the Stellar Developer Foundation.
The official CLI can be found here https://github.com/stellar/soroban-cli
Should this become useful, I am happy to transfer it as well to the SDF org!
