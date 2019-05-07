# External Archive Data Access

Tools to access VO data services

# Install

If you use `pip`, you can simply copy-n-paste the latest [release](https://github.com/chbrandt/eada/releases) URL (currently, `0.9.7.3`):
```bash
$ pip install https://github.com/chbrandt/eada/archive/0.9.7.3.tar.gz
```

If `pip` is not an option for you, manually download and unpack the latest [release](https://github.com/chbrandt/eada/releases) and launch the setup script from inside the package:
```bash
$ python setup.py install
```


## Dependencies

EADA should work with either Python 2 or 3.
It has a couple of dependencies, which by the way you should manually install as
the setup process is designed to satisfy them automatically:
* [Astropy](http://www.astropy.org/)
* [PyVO](https://github.com/pyvirtobs/pyvo)


## Services

Currently there is support for accessing Simple Cone Search(SCS) and Simple Spectral Access(SSA)
services. For each of them there is a config (\*.cfg) file, containing the relation of servers
and columns to retrieve on each search.


## How to use

### API

### Command line interface

#### List known services (per type)
```bash
$ vos list --help
```

```bash
$ vos list epn-tap [--filter]
```

```bash
$ vos list scs [--filter]
```

#### Update the list of known services (per type)
```bash
$ vos update --help
```

```bash
$ vos update {epn-tap | scs} --help
```

```bash
$ vos update epn-tap [options]
```

```bash
$ vos update scs [options]
```

#### Get info about a service (per type)
```bash
$ vos info --help
```

```bash
$ vos info epn-tap <service-name>
```

```bash
$ vos info scs <service-name>
```

#### Download data from a service
```bash
$ vos fetch --help
```

```bash
$ vos fetch epn-tap --help
```

```bash
$ vos fetch scs --help
```

```bash
$ vos fetch epn-tap <service-name> [options]
```

```bash
$ vos fetch scs <service-name> [options]
```


Scripts for each of the protocols -- SCS and SSA -- are available. After installing the package,
```bash
$ conesearch --help
```
and
```
$ specsearch --help
```
should give you all the possibilites on parameters to use.
Both services' basic input arguments are an _object position_(__RA,DEC__) in degrees, a search radius,
and the server/service name or URL to query.

Config files
------------

Each service -- SCS, SSA -- has its own config file -- conesearch.cfg and specsearch.cfg, resp.
Config files are INI-like files where a list of servers and the columns to retrieve can be preset.
The config files are placed together with the respective executables.

/.\
