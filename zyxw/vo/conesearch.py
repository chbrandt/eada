#-*- coding:utf-8 -*-

TIMEOUT=20

def conesearch(ra,dec,radius,db_url,timeout=None):
    """
    Search for objects inside the 'radius' around ('ra','dec,)
    
    Input:
     - ra      : right ascension (degrees)
     - dec     : declination (degrees)
     - radius  : search radius, value in degrees
     - db_url  : url (address) of the service to query/retrieve
     - timeout : amout of time in seconds to wait for a response
    """
    
    from pyvo.dal import scs
    from pyvo.dal import query

    try:
        if timeout is None and TIMEOUT:
            timeout = TIMEOUT
        query.setparam('timeout',timeout)
    except:
        logwrn("'timeout' parameter not set on query.")

    logdbg("Position (%s,%s) and radius, in degrees, (%s)", ra, dec, radius)
    try:
        res = scs.search( db_url, (ra,dec), radius, verbosity=3)
    except query.DALServiceError, e:
        logging.exception("Exception raised: %s", e)
        print "Service not responding"
        return None
    except query.DALQueryError, e:
        logging.exception("Exception raised: %s", e)
        print "Query returned error"
        return None
        
    if res.nrecs is 0:
        logerr("No sources were found for (ra:%s, dec:%s ;radius:%s)", ra, dec, radius)
    else:
        logdbg("Number of sources found: %d", res.nrecs)
        
    return res

# --
def main(ra,dec,radius,db_url,columns):
    """
    Do the input verifications and check the output of the query.
    
    Input:
        - ra      : right ascension (degree)
        - dec     : declination (degree)
        - radius  : radius to search for objects
        - db_url  : url (address) of the service to query/retrieve
        - columns : columns of interest to get from the output table
    """
    
    srcsTab = conesearch(ra,dec,radius,db_url,TIMEOUT)
    if srcsTab is None:
        logging.critical("Search failed to complete. DAL raised an error.")
        print "Failed."
        return None
    
    nrecs = srcsTab.nrecs
    nrows = srcsTab.votable.nrows
    assert(nrows==nrecs)
    tab = srcsTab.votable.to_table()
    
    # Garantee we don't have empty column names..
    cols = [ c for c in columns if c.replace(' ','') != '' ]
    if len(cols) > 0:
        tab.keep_columns(cols)
    else:
        logwrn("Since no column names were given, output will contain all catalog' columns.")
    
    if tab:
        tab = filterColumns(tab,cols)
    
    return tab,nrows

# --

def filterColumns(table,cols):
    """Filter the columns of the table retrieved"""
    
    if len(cols) > 0:
        tab = table
        from astropy.table.table import Table
        table = Table()
        for c in cols:
            table.add_column(tab.columns[c])
    
    return table

# --

