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
@click.option('--filename', default=None,
                help="Output filename. Defaults to 'service'.")
@click.option('--format', default='csv', show_default=True,
                type=click.Choice(['csv', 'html']),
                help="Output file format.")
@click.option('--limit', default=10, show_default=True,
                help="Limit the size of records returned.")
@click.option('--random', default=False, is_flag=True,
                help="Random sample? Defaults to 'TOP(limit)'.")
@click.option('--where', default=None, type=str,
                help="A 'where' filter clause (see '--help')")
def fetch(service, limit, random, where, filename, format):
    """
    Fetch data from 'service'.

    The `where` filter is a ADQL/SQL 'where' clause. For example, if you want
    records of `dataproduct_type` "image" from the "mars" `body`, `where` is:
    ```
    dataproduct_type="im" & body="mars"
    ```
    """
    table = epntap.fetch(service, limit=limit, random=random, where=where)
    if table is None or len(table)==0:
        print("No records found.")
        return
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
