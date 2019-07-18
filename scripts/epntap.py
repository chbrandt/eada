import click

from eada import _utils
from eada import epntap

_CACHE_DIR = './'

@click.group()
def cli():
    """
    EPN-TAP services query
    """
    # click.echo('CLI!')

@cli.command()
def list():
    """
    Print local list of services
    """
    epntap.list()

@cli.command()
@click.argument('service')
def add(service):
    """
    Add a service to local
    """
    epntap.add(service)

@cli.command()
@click.argument('service')
def remove(service):
    """
    Remove 'service' from local
    """
    epntap.remove(service)

@cli.command()
@click.argument('service')
def about(service):
    """
    Print service information
    """
    epntap.about(service)

@cli.command()
def update(cache_dir=_CACHE_DIR):
    """
    Update local cache of services
    """
    epntap.update()
    # _utils.write_cache(res)

@cli.command()
@click.argument('service')
@click.option('--filename', default=None, help="Defaults to 'service' if None")
@click.option('--format', default='csv', type=click.Choice(['csv', 'html']))
def fetch(service, filename, format):
    """
    Fetch data from service
    """
    table = epntap.fetch(service)
    if filename is None:
        filename = '{!s}.{!s}'.format(service, format)
    table.write(filename, format=format, overwrite=True)

@cli.command()
@click.argument('keyword')
def search(keyword):
    """
    Search for keyword among services metadata
    """
    pass


# if __name__ == '__main__':
#     cli()
