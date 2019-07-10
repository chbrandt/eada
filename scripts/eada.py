import click
import os

import eada

# Commands that will be available as subcommands of this cli/eada
# This commands are associated to same-named python modules; it's
# defined in Subcommands class
#
COMMANDS = ['epntap', 'scs']


class Subcommands(click.MultiCommand):
    """
    Implement COMMANDS as subcommands
    """
    def list_commands(self, ctx):
        rv = COMMANDS
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        # define python module from COMMANDS names
        fn = os.path.join(os.path.dirname(__file__), name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


@click.command(cls=Subcommands)
def cli():
    pass
