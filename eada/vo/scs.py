#-*- coding:utf-8 -*-

from eada import *
from eada.io import table

Aux = table.Aux


def search(ra,dec,radius,url,columns=[]):
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
     - VOTable (py:class:`~astropy.table.table.Table`)
         Retrieved table, 'columns'-filtered. 'None' is returned in case of error

    """
    logging.info(Doc.synopsis(search))
    logging.info("Position (%s,%s) and radius (%s), in degrees", ra, dec, radius)
    logging.info("URL (%s) and columns (%s)", url, columns)

    from pyvo.dal import scs as voscs
    from pyvo.dal import query

    tab = None
    try:

        _tab = voscs.search( url, (ra,dec), radius, verbosity=3)

        tab = _tab
    except query.DALServiceError as e:
        logging.exception("DALServiceError raised: %s", e)
    except query.DALQueryError as e:
        logging.exception("DALQueryError raised: %s", e)
    except Exception as e:
        logging.exception("Exception raised: %s", e)

    if tab is None:
        logging.error("Search failed to complete. Service not working properly. Exiting")
        return None

    nobjs = tab.nrecs
    assert(nobjs == tab.votable.nrows)

    tabvo = tab.votable.to_table()
    if tabvo is None:
        logging.error("Retrieved table is Null. Exiting")
        return None

    # --- Enclosure the Table importing for assert reasons only ---
    def _assert_(table):
        from astropy.table.table import Table
        return isinstance(table,Table)
    assert _assert_vot(tabvo)
    # ---

    # Garantee we don't have empty column names and names that match tble ones..
    if columns:
        cols = Aux.filter_columns(tabvo,columns)
        tabvo.keep_columns(cols)

    logging.info("Retrieved table has %d objects, %d columns." % (nobjs,len(tabvo.colnames)))
    return tabvo
