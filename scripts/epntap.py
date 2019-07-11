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
def update(cache_dir=_CACHE_DIR):
    """
    Update local cache of services
    """
    res = _epntap.update()
    _utils.write_cache(res)

@cli.command()
@click.argument('service')
def about(service):
    """
    Print service information
    """
    click.echo('info {}'.format(service))

@cli.command()
@click.argument('service')
def fetch(service):
    """
    Fetch data from service
    """
    click.echo('fetch {}'.format(service))

@cli.command()
@click.argument('keyword')
def search(keyword):
    """
    Search for keyword among services metadata
    """
    pass

@cli.command()
@click.argument('service')
def remove(service):
    """
    Remove 'service' from local
    """
    pass

@cli.command()
@click.argument('service')
def about(service):
    """
    Print information about 'service'
    """
    pass

@cli.command()
@click.argument('service')
def fetch(service):
    """
    Fetch data from 'service'
    """
    pass

# if __name__ == '__main__':
#     cli()
