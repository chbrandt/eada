import json
import pandas as pd
from pyvo import tap

# _QUERY_REGISTRY = "SELECT * FROM rr.res_table WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0'"
# _QUERY_REGISTRY = "SELECT ivoid FROM rr.res_table WHERE table_utype LIKE 'ivo://vopdc.obspm/std/epncore%'"
# _QUERY_REGISTRY = "SELECT rr.res_table.ivoid, access_url, table_name, short_name, res_title, res_description, reference_url, role_name, base_role AS rol_name FROM rr.res_table NATURAL JOIN rr.resource NATURAL JOIN rr.interface NATURAL JOIN rr.res_role WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0' AND ivoid NOT IN (SELECT rr.capability.ivoid FROM rr.capability WHERE cap_type = 'tr:tableaccess')"
_QUERY_REGISTRY = "SELECT * FROM rr.res_table NATURAL JOIN rr.resource NATURAL JOIN rr.interface NATURAL JOIN rr.res_role WHERE table_utype = 'ivo://vopdc.obspm/std/epncore#schema-2.0' AND ivoid NOT IN (SELECT rr.capability.ivoid FROM rr.capability WHERE cap_type = 'tr:tableaccess')"

def update():
    accessurl = 'http://voparis-rr.obspm.fr/tap'
    service = tap.TAPService(accessurl)

    query = _QUERY_REGISTRY
    res = service.search(query)

    result_table = res.to_table()
    return result_table.to_pandas()


def list_services(query_count=False, schema_only=False,
                    registry_file=None):
    """
    List available services
    """
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
