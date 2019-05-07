import click
import os

here = os.path.dirname(__file__)

class MyCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = ['epntap','scs']
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(here, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']

@click.command(cls=MyCLI)
def cli():
    pass
