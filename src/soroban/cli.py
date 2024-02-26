import soroban
import typer


app = typer.Typer()


@app.command()
def invoke(
    contract_id: str,
    function_name: str,
    source_account: str = None,
):
    identity = soroban.Identity(secret_key=source_account)
    res = soroban.invoke(
        contract_id=contract_id, function_name=function_name, source_account=identity
    )
    print(res)


# only needed because we have a single command
@app.callback()
def callback():
    pass
