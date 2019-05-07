import click

# import _utils
# import _epntap

_CACHE_DIR = './'

@click.group()
def cli():
    """Simple program that greets NAME for a total of COUNT times."""
    # click.echo('CLI!')

@cli.command()
def update(cache_dir=_CACHE_DIR):
    # res = _epntap.update()
    # _utils.write_to_cache(res)
    click.echo('update')

@cli.command()
def list():
    # res = _epntap.list_services()
    # print(res)
    click.echo('list')

@cli.command()
def fetch():
    click.echo('fetch')

# if __name__ == '__main__':
#     cli()
