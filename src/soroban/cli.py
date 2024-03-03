import json

from typing_extensions import Annotated

import soroban
import typer


app = typer.Typer()


@app.command()
def invoke(
    contract_id: str,
    function_name: str,
    source_account: str = None,
    args: Annotated[typer.FileBinaryRead, typer.Option()] | None = None,
):
    identity = soroban.Identity(secret_key=source_account)

    if args is not None:
        args = json.load(args)
        args = soroban.Parameters(args=args).model_dump()

    res = soroban.invoke(
        contract_id=contract_id,
        function_name=function_name,
        source_account=identity,
        args=args,
    )
    print(res)


# only needed because we have a single command
@app.callback()
def callback():
    pass
