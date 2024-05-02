import pathlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_serializer, model_validator, HttpUrl
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
    seed_phrase: str | None = None
    secret_key: str | None = None
    public_key: str | None = None
    keypair: Keypair | None = None

    model_config = SettingsConfigDict(
        env_file=[
            "identity.toml",
            pathlib.Path(".soroban") / "identity" / "identity.toml",
        ]
    )

    @model_validator(mode="after")
    def load_keys(self) -> "Identity":
        if (
            self.keypair is None
            and self.secret_key is None
            and self.seed_phrase is None
        ):
            raise ValueError(
                "Either provide a seed phrase, secret key or a Keypair object. Also look"
                "in 'identity.toml'"
            )
        if self.keypair is not None:
            self.secret_key = self.keypair.secret
        elif self.secret_key is not None:
            self.keypair = Keypair.from_secret(self.secret_key)
        else:
            self.keypair = Keypair.from_mnemonic_phrase(self.seed_phrase)
        self.public_key = self.keypair.public_key
        return self

    @classmethod
    def from_source_account(
        cls, account: Keypair | str | pathlib.Path | None = None
    ) -> "Identity":
        if account is None:
            identity = Identity()
        elif (
            isinstance(account, str) and account.startswith("S") and len(account) == 56
        ):
            identity = Identity(secret_key=account)
        elif isinstance(account, (str, pathlib.Path)):
            fname = _load_configuration(account, "identity")
            identity = Identity(_env_file=fname)
        else:
            identity = Identity(keypair=account)
        return identity


class NetworkConfig(BaseSettings):
    # https://horizon.publicnode.org
    horizon_url: HttpUrl = HttpUrl("https://horizon-testnet.stellar.org")
    rpc_url: HttpUrl = HttpUrl("https://soroban-testnet.stellar.org")
    network_passphrase: str = Network.TESTNET_NETWORK_PASSPHRASE
    base_fee: int = 100

    model_config = SettingsConfigDict(
        env_file=["network.toml", pathlib.Path(".soroban") / "network" / "network.toml"]
    )

    @model_validator(mode="after")
    def load_urls(self) -> "NetworkConfig":
        # or use the Annotated construction
        self.horizon_url = str(self.horizon_url)
        self.rpc_url = str(self.rpc_url)
        return self

    @classmethod
    def from_network(cls, network: str | pathlib.Path | None = None) -> "NetworkConfig":
        if network is None:
            network = NetworkConfig()
        elif isinstance(network, (str, pathlib.Path)):
            fname = _load_configuration(network, "network")
            network = NetworkConfig(_env_file=fname)
        return network


class Argument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: str
    value: int | bytes | str | xdr.SCVal


class Parameter(Argument):
    name: str
    value: int | bytes | str | xdr.SCVal | list[Argument | xdr.SCVal]

    @model_validator(mode="after")
    def value_to_scval(self) -> "Parameter":
        if isinstance(self.value, list):
            self.value = [self._value_to_scval(val) for val in self.value]
        self.value = self._value_to_scval(self)
        return self

    @staticmethod
    def _value_to_scval(value: Argument | xdr.SCVal):
        if isinstance(value, Argument) and not isinstance(value.value, xdr.SCVal):
            value = getattr(scval, f"to_{value.type}")(value.value)
        return value


class Parameters(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    args: list[Parameter]

    @model_serializer
    def ser_model(self) -> list[xdr.SCVal]:
        return [arg.value for arg in self.args]
