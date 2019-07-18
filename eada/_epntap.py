import json
import pandas as pd
from pyvo import tap
from timeout_decorator import timeout_decorator

from ._manager import Manager
from .config import Cache, Local
from .vo import epntap

# _QUERY_REGISTRY = "SELECT * FROM rr.res_table WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0'"
# _QUERY_REGISTRY = "SELECT ivoid FROM rr.res_table WHERE table_utype LIKE 'ivo://vopdc.obspm/std/epncore%'"
# _QUERY_REGISTRY = "SELECT rr.res_table.ivoid, access_url, table_name, short_name, res_title, res_description, reference_url, role_name, base_role AS rol_name FROM rr.res_table NATURAL JOIN rr.resource NATURAL JOIN rr.interface NATURAL JOIN rr.res_role WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0' AND ivoid NOT IN (SELECT rr.capability.ivoid FROM rr.capability WHERE cap_type = 'tr:tableaccess')"
_QUERY_REGISTRY = "SELECT * FROM rr.res_table NATURAL JOIN rr.resource NATURAL JOIN rr.interface NATURAL JOIN rr.res_role WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0' AND ivoid NOT IN (SELECT rr.capability.ivoid FROM rr.capability WHERE cap_type = 'tr:tableaccess')"


class EPNTAP(Manager):
    def __init__(self):
        super()
        self._cache = Cache('epntap')
        self._local = Local('epntap')

    def update(self):
        """
        Update the list of services (in cache)
        """
        import os
        _here = os.path.dirname(os.path.abspath(__file__))
        registry_file = os.path.join(_here, 'virtualRegistry.json')
        with open(registry_file, 'r') as fp:
            import json
            js = json.load(fp)
            services = js['services']
        cache_dir = self._cache.path
        for s in services:
            filename = os.path.join(cache_dir, s['schema']+'.json')
            with open(filename, 'w') as fp:
                json.dump(s, fp)

        # What it should -- and will some day -- do to update in-cache services
        if False:
            accessurl = 'http://voparis-rr.obspm.fr/tap'
            service = tap.TAPService(accessurl)

            query = _QUERY_REGISTRY
            res = service.search(query)

            result_table = res.to_table()
            return result_table.to_pandas()

    def fetch(self, service, limit=10):
        resource = self.resource(service)
        return epntap.fetch(url=resource['accessurl'],
                            table=resource['schema'],
                            limit=limit)

    def add(self, service):
        """
        Add a service (from cache) to local
        """
        super().add(service)

    def remove(self, service):
        """
        Remove a service from local
        """
        super().remove(service)

    def about(self, service):
        """
        Print information about a service
        """
        super().about(service)

    def list(self):
        # query_count=False, schema_only=False, registry_file=None):
        """
        List available services
        """
        super().list()

        if False:
            from eada import _utils
            registry_file = _utils.path_registry_cache()

            # File base containing the list of VESPA services
            #
            print(registry_file)
            try:
                with open(registry_file, 'r') as fp:
                    registry_list = json.load(fp)
            except FileNotFoundError:
                print("List of services is empty, try 'update' the cache")
                return None

            # titles = []
            # schemas = []
            # print(type(registry_list))
            # for service in registry_list:
            #     try:
            #         title = service['table_title']
            #         schema = service['table_name']
            #     except:
            #         continue
            #     else:
            #         titles.append(title)
            #         schemas.append(schema)
            #
            # return {'title':titles, 'schema':schemas}

            # df = pd.read_json(json.dumps(registry_list['services']), orient='records')
            df = pd.read_json(json.dumps(registry_list), orient='records')
            print(df)
            #
            # output_fields = ['schema']
            # if schema_only:
            #     return df[output_fields]
            #
            # if query_count:
            #     output_fields.append('count')
            #     def query_serv(row):
            #         return _query_serv(row['schema'], row['accessurl'],)
            #     df['count'] = df.apply(query_serv, axis=1)
            #     # assert any(df['count'].isnull()), "We should not be seeing this!"
            #     df['count'].astype(int, inplace=True)
            #
            # output_fields.append('title')
            #
            # return df[output_fields]

# ===============================================================
# This script is meant to download data from VO/EPN-TAP archives.
# We will need a list of services, a default list is provided by:
_DEFAULT_SERVICES_LIST_ = 'virtualRegistry.json'
# ===============================================================
from os import path

here = path.abspath(path.dirname(__file__))
_DEFAULT_SERVICES_LIST_ = path.join(here, _DEFAULT_SERVICES_LIST_)

def update_fake():
    """
    Update internal list of available services
    """
    import json
    import pandas as pd

    registry_list = read_registry_file()
    df = pd.read_json(json.dumps(registry_list['services']), orient='records')

    output_fields = ['schema']

    output_fields.append('count')
    def query_serv(row):
        return _query_serv(row['schema'], row['accessurl'],)
    df['count'] = df.apply(query_serv, axis=1)
    # assert any(df['count'].isnull()), "We should not be seeing this!"
    df['count'].astype(int, inplace=True)

    output_fields.append('title')

    return df[output_fields]

def read_registry_file(registry_file = _DEFAULT_SERVICES_LIST_):
    # File base containing the list of VESPA services
    #
    with open(registry_file, 'r') as fp:
        services_list = json.load(fp)
    return services_list


_TIMEOUT_ = 10
@timeout_decorator.timeout(_TIMEOUT_)
def _query_timeout(serv, query):
    return serv.search(query)


def _query_serv(schema, accessurl):
    def _init_query_struct():
        """
        Setup a query object to simplify my life
        """
        from collections import namedtuple
        Query = namedtuple('Query', ['SELECT','FROM','COUNT','TOP','WHERE'])
        Query.SELECT = 'SELECT'
        Query.FROM_schema = 'FROM {schema!s}.epn_core'
        Query.COUNT = 'COUNT(*)'
        Query.TOP_limit = 'TOP {limit:d}'
        Query.WHERE_fraction = 'WHERE rand() <= {fraction:f}'
        return Query
    q = _init_query_struct()
    query = ' '.join([q.SELECT,q.COUNT,q.FROM_schema]).format(schema=schema)
    serv = tap.TAPService(accessurl)
    try:
        t = _query_timeout(serv, query)
        count = int(t.to_table()[0][0])
    except:
        count = _NULL_INT_
    return count
