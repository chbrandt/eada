# External Archive Data Access

Tools to access VO data services


Install
=======

You can install `eada` directly using the URL from one of the package [releases](https://github.com/chbrandt/eada/releases).
Use the _latest_ release.

Currently, the latest version is `v1.1`; To install it we simply do:

```
$ pip install https://github.com/chbrandt/eada/archive/v1.1.zip
```

 This will install the python interface and (shell) executable scripts in the proper places.


Dependencies
------------

 * [astropy](http://www.astropy.org/)
 * [pyvo](https://github.com/pyvirtobs/pyvo)


Services
========

 Currently there is support for accessing Simple Cone Search(SCS) and Simple Spectral Access(SSA)
 services. For each of them there is a config (\*.cfg) file, containing the relation of servers
 and columns to retrieve on each search.


How to use
==========

Command line interface
----------------------

 Scripts for each of the protocols -- SCS and SSA -- are available. After installing the package,
 ```
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

[]
