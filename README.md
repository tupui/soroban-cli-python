# Soroban CLI

CLI and functions to call Soroban contracts with Python.

```
pip install soroban
```

This provides a simple way to call contracts without needing to install the
Rust SDK and is a higher level interface compared to using the Python SDK.

```python
import soroban

soroban.invoke("AAAA...", "increment")
```

Identity and Network configurations are automatically pulled from the global
or local configuration.

> Note: this repository has no affiliation with the Stellar Developer Foundation.
> The official CLI can be found here https://github.com/stellar/soroban-cli
> Should this become useful, I am happy to transfer it as well!
