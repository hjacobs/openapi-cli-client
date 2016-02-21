import click
import os
from openapi_cli_client.cli import generate_cli

def test_generate_cli():
    cli = generate_cli(os.path.join(os.path.dirname(__file__), 'fixtures/petstore.yaml'))
    assert isinstance(cli, click.Group)
    assert 'pets' in cli.commands
    commands = cli.commands['pets'].commands
    assert 4 == len(commands)
    assert 'list' in commands
    assert 'get' in commands
    assert 'delete' in commands
    assert 'update' in commands
