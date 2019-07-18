import os
import json
from glob import glob
# from appdirs import AppDirs


class AppDirs(object):
    """This is a mock AppDirs, for test purposes"""

    def __init__(self, appname, author=None, version=None):
        assert len(appname) > 0 and appname != '/'
        self._basedir = '/tmp'
        self._appname = appname
        self._version = version
        self.initialize_dirs()

    def initialize_dirs(self):
        # Guarantee data and cache exist
        _makedir(self.user_data_dir)
        _makedir(self.user_cache_dir)

    def _assembly(self, data_type):
        return os.path.join(self._basedir,
                            self._appname,
                            self._version,
                            data_type)

    @property
    def user_data_dir(self):
        return self._assembly('local')

    @property
    def user_cache_dir(self):
        return self._assembly('cache')


def _makedir(dirname):
    import errno
    import os

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


class _Dirs(object):
    _services = None

    def __init__(self, service_type):
        self._dirs = AppDirs(appname=__package__, version=service_type)

    def _read(self):
        if self._services is None:
            self._services = [os.path.splitext(f)[0] for f in _read(self)]

    @property
    def services(self):
        self._read()
        return self._services

    def file(self, service):
        filename = glob(os.path.join(self.path, '.'.join([service,'json'])))
        assert len(filename) <= 1
        if len(filename):
            return filename[0]
        return None

    def read_service(self, service):
        filename = self.file(service)
        if filename is None:
            print("error: resource '{!s}' not found".format(service))
            return None
        with open(filename, 'r') as fp:
            js = json.load(fp)
        return js


class Local(_Dirs):
    @property
    def path(self):
        return self._dirs.user_data_dir


class Cache(_Dirs):
    @property
    def path(self):
        return self._dirs.user_cache_dir


def _read(obj):
    path = obj.path
    files = glob(os.path.join(path, "*.json"))
    files = [os.path.basename(f) for f in files]
    return files
