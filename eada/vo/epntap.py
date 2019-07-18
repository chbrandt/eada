#!/usr/bin/env python

import logging as log
import timeout_decorator
import json
import pandas as pd
from pyvo import tap

# ===============================================================
# This script is meant to download data from VO/EPN-TAP archives.
# We will need a list of services, a default list is provided by:
_DEFAULT_SERVICES_LIST_ = 'virtualRegistry.json'
# ===============================================================

# Directory to put results:
_OUTPUT_DIR_ = 'data'

# Sometimes queries may stale, so let's define a timeout limit (seconds):
_TIMEOUT_ = 9

# For when we expect an integer but nothing is returned (e.g., service down):
_NULL_INT_ = -999

# Set the logging system:
log.basicConfig(level=log.DEBUG)


def read_registry_file(registry_file = _DEFAULT_SERVICES_LIST_):
    # File base containing the list of VESPA services
    #
    import os
    _here = os.path.dirname(os.path.abspath(__file__))
    registry_file = os.path.join(_here,'..',_DEFAULT_SERVICES_LIST_)
    with open(registry_file, 'r') as fp:
        services_list = json.load(fp)
    return services_list


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


def fetch(schema, limit=None, percent=None, columns=None,):
    """
    Download data from EPN-TAP service.
    Mandatory 'option_schema' is one of the schema (i.e, service) defined in '{}'.
    Use 'limit' to limit the number of results (TOP) to download.

    Input:
     - schema : <str>
        Name of EPN-TAP service (without '.epn_core') to query
     - limit: <int> (None)
        Number of records/lines to download to the TOP(limit) records of the table
     - percent: <float> (None)
        Percentage (0:100) of the table RANDOMLY selected
     - registry_file: <str>
        Config (json) filename where "schema" is defined

    Output:
     - Pandas DataFrame with resulting table

    About sampling the results: 'limit' and 'percent' are mutually excludent.
    'limit' has preference over 'percent' (simply because it is cheaper).
    * 'limit': returns the TOP "limit" records of the table;
    * 'percent': eturns a random sample of size ~percent of table.
    """
    option_schema = schema

    services_list = read_registry_file()

    # Schema we want to work with now
    #
    sanity_check_schema = False
    option_accessurl = None
    option_identifier = None
    for service in services_list['services']:
        if service['schema'] == option_schema:
            sanity_check_schema = True
            option_accessurl = service['accessurl']
            option_identifier = service['identifier']
            break

    assert sanity_check_schema is True, \
        "Schema '{}' not found in '{}'".format(option_schema, services_list_filename)

    log.debug("Schema: {}".format(option_schema))

    if not columns:
        option_columns = '*'

    log.debug("Columns: {}".format(option_columns))

    # Set the (TAP) service
    #
    vo_service = tap.TAPService(option_accessurl)

    # Get the data
    #
    query_expr = ['SELECT']

    if limit is not None:
        assert limit > 0, "'limit' expected to be greater than 0"
        query_expr.append('TOP {:d}'.format(limit))

    query_expr.append('{cols!s} FROM {schema!s}.epn_core')

    if percent is not None:
        assert 0 < percent < 100, "'percent' expected to between (0,100)"
        query_expr.append('WHERE rand() <= {fx:f}'.format(fx=percent/100.0))

    query_expr = ' '.join(query_expr)
    query_expr = query_expr.format(cols=option_columns,
                                   schema=option_schema)

    log.debug("Query: {}".format(query_expr))
    # print("QUERY:", query_expr)

    try:
        vo_result = _query_timeout(vo_service, query_expr)
    except:
        return None

    log.debug("Results: {:d}".format(len(vo_result)))
    
    result_table = vo_result.table
    result_df = result_table.to_pandas()
    result_df['service_schema'] = option_schema
    result_df['service_identifier'] = option_identifier
    return result_df


def update():
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


def update():
    df = _update()
    df.to_json('services_list.json')


def show():
    """
    List available services
    """
    import json
    import pandas as pd

    registry_list = read_registry_file()
    df = pd.read_json(json.dumps(registry_list['services']), orient='records')

    output_fields = ['schema']
    output_fields.append('title')
    df = df[output_fields]
    print(df.to_string(index=False))

def _fetch(args):
    epn_schema = args.schema
    number_records = args.limit
    fraction = args.percent

    result_df = fetch(epn_schema, limit=number_records, percent=fraction)
    if result_df is None:
        print("-----")
        print("Error retrieving from '{}' service".format(epn_schema))
        print("-----")
        return

    if not os.path.isdir(_OUTPUT_DIR_):
        os.mkdir(_OUTPUT_DIR_)
    output_dir = os.path.join(_OUTPUT_DIR_, epn_schema)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    number_records = len(result_df)
    output_filename = os.path.join(output_dir, '{0}_{1}.json'.format(epn_schema, number_records))

    output_link = os.path.join(output_dir, '{0}_latest.json'.format(epn_schema))
    if os.path.islink(output_link):
        os.remove(output_link)
    os.symlink(os.path.basename(output_filename), output_link)

    result_df.to_json(output_filename, orient='records')

    print("-----")
    print("Results written to: {}".format(output_filename))
    print("-----")



# if __name__ == '__main__':
#     import sys
#     import os
#     import argparse
#
#     description = """
#     Download data from EPN-TAP services.
#     Use 'list' for the list of services.
#     """
#     parser = argparse.ArgumentParser(description=description, add_help=False)
#     parser.add_argument('-h', '--help', action='help',
#                         help="Use '--help' on subcommands to know more about them")
#
#     subparsers = parser.add_subparsers(title='Subcommands')
#
#     fetching = subparsers.add_parser('fetch', help='Fetch data from a service')
#     fetching.add_argument('schema', help="Name of EPN-Core schema ('schema.epn_core')")
#     fetching.add_argument('--limit', dest='limit', type=int,
#                           help='Limit the number of returned records',
#                           default=None)
#     fetching.add_argument('--percent', dest='percent', type=float,
#                           help='Fraction (in percentile) of table size records to return',
#                           default=None)
#     fetching.set_defaults(func=_fetch)
#
#     listing = subparsers.add_parser('list', help='List schemas')
#     listing.add_argument('--length', dest='count', action='store_true',
#                          help="List services' number of records")
#     listing.add_argument('--minimal', dest='schema_only', action='store_true',
#                          help="List the names of the schema only")
#     listing.set_defaults(func=_list)
#
#     if len(sys.argv) == 1:
#         parser.print_help()
#         sys.exit(0)
#
#     args = parser.parse_args()
#     args.func(args)
