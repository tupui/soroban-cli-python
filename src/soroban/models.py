import pathlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from stellar_sdk import xdr
from stellar_sdk import Keypair, Network, scval

__all__ = ["Identity", "NetworkConfig", "Parameter", "Parameters"]


def _load_configuration(id: str | pathlib.Path, kind: Literal["identity", "network"]):
    id = pathlib.Path(id)
    global_config = pathlib.Path.home() / ".config" / "soroban" / kind / id / ".toml"
    local_config = pathlib.Path(".soroban") / kind / id / ".toml"

    id = pathlib.Path(id)

    if id.is_file():
        return id
    elif local_config.is_file():
        return local_config
    elif global_config.is_file():
        return global_config
    else:
        raise ValueError(f"Cannot find a {kind!r} configuration for {id!r}")


class Identity(BaseSettings):
    secret_key: str | None = None
    public_key: str | None = None
    keypair: Keypair | None = None

    model_config = SettingsConfigDict(env_file="identity.toml")

    @model_validator(mode="after")
    def load_keys(self) -> "Identity":
        if self.keypair is None and self.secret_key is None:
            raise ValueError("Either provide a secret key or a Keypair object.")
        if self.keypair is not None:
            self.secret_key = self.keypair.secret
        else:
            self.keypair = Keypair.from_secret(self.secret_key)
        self.public_key = self.keypair.public_key
        return self

    @classmethod
    def from_source_account(
        cls, account: Keypair | str | pathlib.Path | None = None
    ) -> "Identity":
        if account is None:
            identity = Identity()
        elif isinstance(account, (str, pathlib.Path)):
            fname = _load_configuration(account, "identity")
            identity = Identity(_env_file=fname)
        else:
            identity = Identity(keypair=account)
        return identity


class NetworkConfig(BaseSettings):
    rpc_url: HttpUrl = HttpUrl("https://soroban-testnet.stellar.org:443")
    network_passphrase: str = Network.TESTNET_NETWORK_PASSPHRASE
    base_fee: int = 100

    model_config = SettingsConfigDict(env_file="network.toml")

    @classmethod
    def from_network(cls, network: str | pathlib.Path | None = None) -> "NetworkConfig":
        if network is None:
            network = NetworkConfig()
        elif isinstance(network, (str, pathlib.Path)):
            fname = _load_configuration(network, "network")
            network = NetworkConfig(_env_file=fname)
        return network


class Parameter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: str
    value: int | float | str | xdr.SCVal

    @model_validator(mode="after")
    def value_to_scval(self) -> "Parameter":
        if not isinstance(self.value, xdr.SCVal):
            self.value = getattr(scval, f"to_{self.type}")(self.value)
        return self


class Parameters(BaseModel):
    args: list[Parameter]
