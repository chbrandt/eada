#-*- coding:utf-8 -*-

from eada import *
from eada.io import table

Aux = table.Aux

from astropy.table.table import Table

def conesearch(ra,dec,radius,url,timeout=None):
    """
    Search for objects inside the circle (ra,dec,radius) at given 'url'

    It is supposed to find a conesearch service at the given 'url' address.

    Input:
     - ra      : float
                 right ascension [degrees]
     - dec     : float
                 declination [degrees]
     - radius  : float
                 search radius [degrees]
     - url     : string
                 url of the service to query/retrieve
     - timeout : int
                 time (seconds) to wait for a response

    Output:
     - SCSResults (py:class:`~pyvo.dal.scs.SCSResults`)
         Conesearch service result. 'None' is returned in case of error.

    """
    db_url = url

    logging.debug("Position (%s,%s) and radius (%s), in degrees", ra, dec, radius)
    logging.debug("URL (%s) and timeout (%s)", url, timeout)

    from pyvo.dal import scs
    from pyvo.dal import query

    if timeout and isinstance(timeout,(int,float)):
        timeout = ((timeout*1.0)+0)/1.0 # sanity check
        try:
            query.setparam('timeout',timeout)
        except:
            logging.warning("'timeout' parameter not set on query.")

    res = None
    try:
        res = scs.search( db_url, (ra,dec), radius, verbosity=3)
    except query.DALServiceError as e:
        logging.exception("DALServiceError raised: %s", e)
    except query.DALQueryError as e:
        logging.exception("DALQueryError raised: %s", e)
    except Exception as e:
        logging.exception("Exception raised: %s", e)

    if res is None:
        return None

    return res


def main(ra,dec,radius,url,columns=[]):
    """
    Query Conesearch service and return a 'columns'-filtered table


    Input:
     - ra      : float
                 right ascension [degrees]
     - dec     : float
                 declination [degrees]
     - radius  : float
                 search radius [degrees]
     - url     : string
                 url of the service to query/retrieve
     - columns : list-of-strings
                 name of the collumns to keep in the output table

    Output:
     - Table (py:class:`~astropy.table.table.Table`)
         Retrieved table, 'columns'-filtered. 'None' is returned in case of error

    """
    logging.info(Doc.synopsis(main))
    logging.info("Position (%s,%s) and radius (%s), in degrees", ra, dec, radius)
    logging.info("URL (%s) and columns (%s)", url, columns)

    scsTab = conesearch(ra,dec,radius,url,TIMEOUT)
    if scsTab is None:
        logging.error("Search failed to complete. Service not working properly. Exiting")
        return None

    nobjs = scsTab.nrecs
    assert(nobjs == scsTab.votable.nrows)

    tab = scsTab.votable.to_table()
    if tab is None:
        logging.error("Retrieved table is Null. Exiting")
        return None

    # Garantee we don't have empty column names and names that match tble ones..
    if columns:
        cols = Aux.filter_columns(tab,columns)
        tab.keep_columns(cols)

    logging.info("Retrieved table has %d objects, %d columns." % (nobjs,len(tab.colnames)))
    return tab
