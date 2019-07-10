import os

class Manager(object):
    """
    Base class for service managers
    """
    _cache = None   # Cache dir or cache object
    _local = None   # Local dir or local object

    def read_dir(self, repo):
        assert repo in ('local','cache')
        if repo == 'local':
            dir_ = self._local
        else:
            dir_ = self._cache
        return dir_.read()

    def list(self, count=False, include='all'):
        """
        Print the list available services

        Arguments:
        - detail <string> | 'minimal'
            Verbosity of the listing, options: 'minimal', 'count', 'normal'
        - include <string> | 'all'
            Stage of services to list, options: 'all', 'local', 'remote'
        """
        # Read resources in local and cache
        services_cache = self.read_dir('cache')
        services_cache.sort()
        services_local = set(self.read_dir('local'))
        services = []
        for s in services_cache:
            name = os.path.splitext(s)[0]
            if s in services_local:
                services.append((name, 'Installed'))
            else:
                services.append((name, 'Not-installed'))
        #TODO: check if there are services in local there are *not* in cache

        # print list of services
        for s in services:
            print('{:20}{!s}'.format(s[0],s[1]))

    def update(cls):
        """
        Update the cache of available services
        """
        raise NotImplementedError

    def about(cls, service):
        """
        Print detailed information about a service

        Arguments:
        - service <string>
            Name of the service to get information about
        """
        raise NotImplementedError

    def search(cls, keywords=None):
        """
        Search for services matching 'keywords'

        Arguments:
        - keywords <string>, <list of strings>
            Keywords to look for in services description

        Output:
        - List of service names matching 'keywords'
        """
        raise NotImplementedError

    def add(cls, service):
        """
        Add a service to the local list
        """
        raise NotImplementedError

    def remove(cls, service):
        """
        Remove a service from the local list
        """
        raise NotImplementedError

    def fetch(cls, service, limit=None, random=False):
        """
        Fetch data from 'service'

        Arguments:
        - service <string>
            Name of the service to query
        - limit <int>, <float> | None
            Number of rows returned, if 0<between<1 assume a percentual limit
        - random <bool> | False
            If True, return a random sample of 'limit' rows, otherwise the TOP(limit)

        Output:
        - pandas dataframe with the retrieved rows
        """
        raise NotImplementedError
