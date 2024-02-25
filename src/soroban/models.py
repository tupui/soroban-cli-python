import pathlib

from pydantic import model_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from stellar_sdk import Keypair, Network

__all__ = ["Identity", "NetworkConfig"]


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
            fname = (
                account
                if pathlib.Path(account).is_file()
                else pathlib.Path(".soroban/identity") / account / ".toml"
            )
            identity = Identity(_env_file=fname)
        else:
            identity = Identity(keypair=account)
        return identity


class NetworkConfig(BaseSettings):
    rpc_url: HttpUrl = HttpUrl("https://soroban-testnet.stellar.org:443")
    network_passphrase: str = Network.TESTNET_NETWORK_PASSPHRASE
    base_fee: int = 100

    model_config = SettingsConfigDict(env_file="network.toml")
