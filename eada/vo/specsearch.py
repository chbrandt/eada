#-*- coding:utf-8 -*-

from eada import *

from astropy.table.table import Table
from pyvo.dal.ssa import SSARecord

from eada.io import table
Aux = table.Aux

def main(ra,dec,radius,url,columns=[],format=None,cachedir=None):
    """
    Query SSA service and return a 'columns'-filtered table

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
    logging.info("Position (%s,%s) and radius (%s), in degrees" %(ra, dec, radius))
    logging.info("URL (%s) and columns (%s)"%(url, columns))

    ssaTab = specsearch(ra,dec,radius,url,format=format)
    if ssaTab is None:
        logging.error("Search failed to complete. Service not working properly. Exiting")
        return None

    tables = []
    for rec in ssaTab:
        filecache = Aux.download_spec(rec,dir=cachedir)
        tab = Aux.open_spec(filecache,rec.format)
        if tab is None:
            continue
        if columns:
            tab = Aux.enrich_columns(tab,rec,columns)
        tables.append(tab)

    if len(tables) == 0:
        logging.error("No tables were found. Exiting")
        return None

    tab = Aux.concatenate_tables(tables)

    # tab = ssaTab.votable.to_table()
    # if tab is None:
    #     logging.error("Retrieved table is Null. Exiting")
    #     return None
    #
    # # Garantee we don't have empty column names and names that match tble ones..
    # if columns:
    #     cols = Aux.filter_columns(tab,columns)
    #     tab.keep_columns(cols)
    #
    # # Remove format from columns
    # for col in tab.colnames:
    #     tab[col].format = None

    logging.info("Retrieved table has %d objects, %d columns." % (len(tab),len(tab.colnames)))
    return tab

def specsearch(ra,dec,radius,url,format=None):
    """
    Search for objects inside the circle (ra,dec,radius) at given 'url'

    It is supposed to find a ssap service at the given 'url' address.

    Input:
     - ra      : float
                 right ascension [degrees]
     - dec     : float
                 declination [degrees]
     - radius  : float
                 search radius [degrees]
     - url     : string
                 url of the service to query/retrieve
     - format  : string
                 format of spectra file(s) to be returned

    Output:
     - SSAResults (py:class:`~pyvo.dal.ssa.SSAResults`)
         Conesearch service result. 'None' is returned in case of error.

    """
    # from pyvo.dal import ssa
    from pyvo.dal import SSAService
    from pyvo.dal import query

    if 'fits' in format:
        format = 'image/fits'
    elif 'votable' in format:
        format = 'votable'
    else:
        format = None

    logging.debug("Position (%s,%s) and radius (%s), in degrees" %(ra, dec, radius))

    # q = ssa.SSAQuery(url)
    # q.pos = (ra,dec)
    # q.size = radius
    # if format and format != 'all':
    #     q.format = format
    ssa_service = SSAService(url)

    res = None
    try:
        # res = q.execute()
        res = ssa_service.search(pos=(ra,dec), diameter=radius)
    except query.DALServiceError as e:
        logging.exception("DALServiceError raised: %s"%(e))
    except query.DALQueryError as e:
        logging.exception("DALQueryError raised: %s"%(e))
    except Exception as e:
        logging.exception("Exception raised: %s"%(e))

    return res
