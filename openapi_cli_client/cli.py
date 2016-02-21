import click
import clickclick
import re
import requests
import sys
import yaml

from functools import partial
from bravado_core.spec import Spec
from bravado.client import construct_request
from bravado.requests_client import RequestsClient

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

REPLACEABLE_COMMAND_CHARS = re.compile('[^a-z0-9]+')


def normalize_command_name(s):
    '''
    >>> normalize_command_name('My Pets')
    'my-pets'

    >>> normalize_command_name('.foo.bar.')
    'foo-bar'
    '''
    return REPLACEABLE_COMMAND_CHARS.sub('-', s.lower()).strip('-')


def get_command_name(op):
    if op.http_method == 'get' and '{' not in op.path_name:
        return 'list'
    elif op.http_method == 'put':
        return 'update'
    else:
        return op.http_method


def invoke(op, *args, **kwargs):
    request = construct_request(op, {}, **kwargs)
    c = RequestsClient()
    future = c.request(request)
    future.result()


def sanitize_spec(spec):

    for path, path_obj in list(spec['paths'].items()):
        # remove root paths as no resource name can be found for it
        if path == '/':
            del spec['paths'][path]
    return spec


def generate_cli(spec):
    origin_url = None
    if isinstance(spec, str):
        if spec.startswith('https://') or spec.startswith('http://'):
            origin_url = spec
            r = requests.get(spec)
            r.raise_for_status()
            spec = yaml.safe_load(r.text)
        else:
            with open(spec, 'rb') as fd:
                spec = yaml.safe_load(fd.read())

    spec = sanitize_spec(spec)

    cli = clickclick.AliasedGroup(context_settings=CONTEXT_SETTINGS)

    spec = Spec.from_dict(spec, origin_url=origin_url)
    for res_name, res in spec.resources.items():
        grp = clickclick.AliasedGroup(normalize_command_name(res_name), short_help='Manage {}'.format(res_name))
        cli.add_command(grp)
        for op_name, op in res.operations.items():
            name = get_command_name(op)

            cmd = click.Command(name, callback=partial(invoke, op=op), short_help=op.op_spec.get('summary'))
            for param_name, param in op.params.items():
                if param.required:
                    arg = click.Argument([param.name])
                    cmd.params.append(arg)
                else:
                    arg = click.Option(['--' + param.name])
                    cmd.params.append(arg)

            grp.add_command(cmd)

    return cli


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Missing OpenAPI spec argument\n')
        sys.exit(1)
    cli = generate_cli(sys.argv[1])
    sys.argv = sys.argv[:1] + sys.argv[2:]
    cli()
