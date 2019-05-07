import click

from eada import _utils
from eada import _epntap

_CACHE_DIR = './'

@click.group()
def cli():
    """Simple program that greets NAME for a total of COUNT times."""
    # click.echo('CLI!')

@cli.command()
def update(cache_dir=_CACHE_DIR):
    res = _epntap.update()
    _utils.write_cache(res)

@cli.command()
def list():
    res = _epntap.list_services()
    click.echo(res)

@cli.command()
@click.argument('service')
def info(service):
    click.echo('info {}'.format(service))

@cli.command()
@click.argument('service')
def fetch(service):
    click.echo('fetch {}'.format(service))

# if __name__ == '__main__':
#     cli()
