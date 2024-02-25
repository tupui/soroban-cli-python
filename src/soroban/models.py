from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from stellar_sdk import Keypair

__all__ = ["Identity"]


class Identity(BaseSettings):
    secret_key: str | None = None
    public_key: str | None = None
    keypair: Keypair | None = None

    model_config = SettingsConfigDict(env_file="identity.toml")

    @model_validator(mode='after')
    def load_keys(self) -> 'UserModel':
        if self.keypair is None and self.secret_key is None:
            raise ValueError("Either provide a secret key or a Keypair object.")
        if self.keypair is not None:
            self.secret_key = self.keypair.secret
        else:
            self.keypair = Keypair.from_secret(self.secret_key)
        self.public_key = self.keypair.public_key
        return self
