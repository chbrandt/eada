import os
import shutil

class Manager(object):
    """
    Base class for service managers
    """
    # 'cache' and 'local' are initialized by the children class
    _cache = None   # Cache dir or cache object
    _local = None   # Local dir or local object

    def read_dir(self, repo):
        assert repo in ('local','cache')
        if repo == 'local':
            dir_ = self._local
        else:
            dir_ = self._cache
        return dir_.services

    def read_service(self, service, repo):
        assert repo in ('local','cache')
        if repo == 'local':
            dir_ = self._local
        else:
            dir_ = self._cache
        return dir_.read_service(service)

    def copy_service(self, service, from_dir='cache', to_dir='local'):
        file_cache = self._cache.file(service)
        file_local = os.path.join(self._local.path, os.path.basename(file_cache))
        shutil.copyfile(file_cache, file_local)

    def remove_service(self, service):
        file_local = self._local.file(service)
        os.remove(file_local)

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
            if s in services_local:
                services.append((s, 'Installed'))
            else:
                services.append((s, 'Not-installed'))
        #TODO: check if there are services in local there are *not* in cache

        # print list of services
        for s in services:
            print('{:20}{!s}'.format(s[0],s[1]))

    def add(self, service):
        """
        Add a service to the local list
        """
        sl = set(self.read_dir('local'))
        if service in sl:
            print("Service {!s} already installed".format(service))
            return True

        sc = self.read_dir('cache')
        if service not in sc:
            print("Service {!s} not found.".format(service))
            return False

        return self.copy_service(service)

    def remove(self, service):
        """
        Remove a service from the local list
        """
        sl = set(self.read_dir('local'))
        if service not in sl:
            print("Service {!s} not installed".format(service))
            return True

        return self.remove_service(service)

    def about(self, service):
        """
        Print detailed information about a service

        Arguments:
        - service <string>
            Name of the service to get information about
        """
        content = None
        is_installed = False

        sl = set(self.read_dir('local'))
        if service in sl:
            is_installed = True
            content = self.read_service(service, 'local')
        else:
            sc = set(self.read_dir('cache'))
            if service in sc:
                content = self.read_service(service, 'cache')

        print('Service:', service)
        print('Installed:', 'yes' if is_installed else 'no')
        for k,v in sorted(content.items()):
            print('{!s}: {!s}'.format(k,v))

    def update(cls):
        """
        Update the cache of available services
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
