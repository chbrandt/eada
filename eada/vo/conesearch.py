#-*- coding:utf-8 -*-

from eada import *

from astropy.table import Table

TIMEOUT=10

# --
class Aux:

    @staticmethod
    def filter_columns(table,columns):
        """
        Verify whether given column names do exist in 'table'

         Columns (which is supposed to be a list of column names) should match with
        table's contents. The columns that do not match with table's will simply
        be discarded from the output list.

        Note: empty column name is not allowed and will be discarded.

        Input:
         - table   : py:class:`~astropy.table.table.Table`
         - columns : [str]
             Column names to verify/match against table ones

        Output:
         - [str]
             List of column names matching table' columns.

        """
        assert(isinstance(table,Table))
        assert(isinstance(columns,list))

        tcols = table.colnames
        logging.debug("Table columns: %s" % tcols)

        cols = []
        for i,col in enumerate(columns):
            assert(isinstance(col,str))
            c = col.strip()
            if not c:
                logging.warning("Empty column name at position %d" % i)
                continue
            del c
            if not col in tcols:
                logging.warning("Column name '%s' not found in table" % col)
                continue
            cols.append(col)

        logging.debug("Selected columns: %s" % cols)
        return cols

# --
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

    res = None
    try:
        res = scs.search( db_url, (ra,dec), radius, verbosity=3)
    except Exception as e:
        logging.exception("Exception raised: %s", e)

    return res

# --
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

    nobjs = len(scsTab)
    assert(nobjs == scsTab.votable.nrows)

    tab = scsTab.votable.to_table()
    if tab is None:
        logging.error("Retrieved table is Null. Exiting")
        return None

    # Garantee we don't have empty column names and names that match tble ones..
    if columns:
        cols = Aux.filter_columns(tab,columns)
        tab.keep_columns(cols)

    # Remove format from columns
    for col in tab.colnames:
        tab[col].format = None

    logging.info("Retrieved table has %d objects, %d columns." % (nobjs,len(tab.colnames)))
    return tab
