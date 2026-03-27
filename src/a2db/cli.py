import click

from a2db import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, package_name="a2db")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """a2db — Agent-to-Database. Query databases from CLI or MCP."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("connection_string")
def connect(connection_string: str) -> None:
    """Test database connection."""
    click.echo(f"Connecting to: {connection_string}")
