import click
import clickclick
import re
import sys
import yaml

from bravado_core.spec import Spec

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


def generate_cli(spec):
    if isinstance(spec, str):
        with open(spec, 'rb') as fd:
            spec = yaml.safe_load(fd.read())

    cli = clickclick.AliasedGroup(context_settings=CONTEXT_SETTINGS)

    spec = Spec.from_dict(spec)
    for res_name, res in spec.resources.items():
        grp = clickclick.AliasedGroup(normalize_command_name(res_name), short_help='Manage {}'.format(res_name))
        cli.add_command(grp)
        for op_name, op in res.operations.items():
            print(op.__dict__)
            name = get_command_name(op)
            cmd = click.Command(name, short_help=op.op_spec.get('summary'))
            for param_name, param in op.params.items():
                print(param.__dict__)
                if param.required:
                    arg = click.Argument([param.name])
                    cmd.params.append(arg)
                else:
                    arg = click.Option(['--' + param.name])
                    cmd.params.append(arg)

                print(param)
            grp.add_command(cmd)
        print(cli.__dict__)
        #setattr(cli, res_name.lower(), cli.group())

    return cli


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Missing OpenAPI spec argument\n')
        sys.exit(1)
    cli = generate_cli(sys.argv[1])
    sys.argv = sys.argv[:1] + sys.argv[2:]
    cli()
