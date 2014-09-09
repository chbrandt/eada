#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import string
import logging
logerr = logging.error
logwrn = logging.warning
logdbg = logging.debug
import warnings
warnings.simplefilter('ignore')

desc = """
    This script searchs for sources in a given position (RA,DEC) and radius (R) 
    in a given catalog. To see the available catalogs use the '--list' option.
"""

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
        if timeout is None:
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
    
    srcsTab = conesearch(ra,dec,radius,db_url,2)
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

def list_catalogs(cp):
    """List the available catalogs"""

    for k,d in cp.iteritems():
        print k
        for c,v in d.items():
            print "| %-10s : %s" % (c,v)
        print ""

# --

def availableCatalogs():
    """
    Get the names of the available catalogs
    """
    cats = [ 'sdss-test','ukidss-test' ]
    return cats
    
def setupParserOptions(parser):
    """
    Define command line options
    """
    
    parser.add_argument('--db', dest='dbfile', metavar='filename', nargs='?',
                        action='store', default='./conesearch.ini',
                        required=True,
                        help="DB/Config filename (ini file).")

    parser.add_argument('--nolog', action='store_true',
                        help="Do *not* log the events of the script. By default all events are written to 'conesearch.log' file.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                        help="Print the list os catalogs available for the search.")
    group.add_argument('--catalog', dest='cat', metavar='CATALOG',
                        choices=availableCatalogs(),
                        help="Catalog to search for data. To see your choices use the '--list' option.")
    group.add_argument('--url', dest='url',
                        help="Service URL to query. To see some options use the\
                         '--list' option.")
                        
    conesearch = parser.add_argument_group('Conesearch','Arguments for searching catalogues.')
    conesearch.add_argument('--ra', dest='ra', type=float, default=0,
                            help="Right Ascension of the object (in degrees by default)")
    conesearch.add_argument('--dec', dest='dec', type=float, default=0,
                            help="Declination of the object (in degrees by default)")
    conesearch.add_argument('--radius', type=float, dest='radius', default=0.00001,
                            help="Radius (around RA,DEC) to search for object(s)",)
    conesearch.add_argument('--runit', dest='runit', metavar='unit', default='arcsec',
                            help="Unit used for radius value. Choices are 'degree',\
                             'arcmin','arcsec'.")

    conesearch.add_argument('--columns', dest='cols', metavar='fieldname', nargs='*',
                            help="Columns to get from the retrieved catalog. The\
                             argument 'asdc' will output a preset of columns, suitable for ASDC.\
                             If not given, all columns will be output.")

    conesearch.add_argument('--short', action='store_true',
                            help="Just outputs if at least one source was found.")
                        
    conesearch.add_argument('-o','--outfile', dest='outfile', nargs='?', const='', 
                            default=None, help="Filename to write the output, CSV format table file.")

    return parser

# --

def argumentsOK(args):
    """Check if basic arguments were given"""

    OK = True
    if args.ra is None:
        print(" RA not provided.")
        OK = False
    if args.dec is None:
        print(" DEC not provided.")
        OK = False
    if args.radius is None:
        print(" Radius not provided.")
        OK = False
    if args.runit is None:
        print(" Radius unit (runit) not provided.")
        OK = False
    if not args.dbfile:
        print(" DB/config file not provided.")
        OK = False
    if not (args.cat or args.url):
        print(" Catalog/url not provided.")
        OK = False

    return OK

# --

def parseArguments(args,cp):
    
    from astropy import units
    
    ra = args.ra
    dec = args.dec
    logdbg('RA:%s , DEC:%s', ra, dec)
    
    radius = args.radius
    ru = ''
    if args.runit == 'degree':
        ru = units.degree
    elif args.runit == 'arcmin':
        ru = units.arcmin
    elif args.runit == 'arcsec':
        ru = units.arcsec
    else:
        logerr("Radius' unit is not valid. Use 'degree', 'arcmin' or 'arcsec'.")
        sys.exit(1)
    rad = radius*ru
    logdbg('Radius %s', rad)
    radius = rad.to(units.degree).value # convert the given radius to degrees
    del rad

    assert(cp)
    assert(args.cat or args.url)
    if not args.url and args.cat not in cp.keys():
        logging.critical("Wrong catalog name: %s", args.cat)
        print "Given catalog ('%s') is not known. Try a valid one (-h)." % (args.cat)
        print "Finishing here."
        sys.exit(1)

    if args.cat:
        cat = args.cat
        url = cp.get(cat)['url']
        logdbg("Catalog (%s) url: %s", cat, url)
    else:
        url = args.url
        logdbg("URL to search for sources: %s", url)

    if args.cols:
        if 'asdc' in args.cols:
            if args.url:
                cols = []
            else:
                dcat = cp.get(cat)
                if dcat.has_key('columns'):
                    cols = dcat.get('columns')
                    cols = string.split(cols,',')
                else:
                    cols = []
        else:
            cols = args.cols
    else:
        cols = []
    logdbg("Columns to output: %s", cols)

    return ra,dec,radius,url,cols


# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=desc)
    parser = setupParserOptions(parser)
    
    # Parse the arguments
    args = parser.parse_args()
    
    import os
    from zyxw.io import config
    if args.dbfile:
        dbfile = os.path.abspath(args.dbfile)
    else:
        sys.exit("No DB file given. Use '--help' for more information.")
    cp = config.read_ini(dbfile)

    if args.list:
        list_catalogs(cp)
        sys.exit(0)

    if not argumentsOK(args):
        sys.exit(1)
        
    if not args.nolog:
        logging.basicConfig(filename='conesearch.log', filemode='w',
                            format='[%(filename)s:%(funcName)20s] %(message)s',
                            level=logdbg)
    else:
        logging.setlevel(logging.NOTSET)

    # Parse the arguments
    ra,dec,radius,url,cols = parseArguments(args,cp)
    
    # Now, the main function does the search and columns filtering...
    out = main(ra,dec,radius,url,cols)
    if not out is None:
        table,nrows = out
    else:
        if args.short:
            print "Failed"
        else:
            print "---"
            print "\033[91mNot able to access data for source in archive %s\033[0m" % (url)
            print "---"
        sys.exit(1)
    
    if args.short:
        print "Number of sources found %d" % nrows
        sys.exit()
    
    if nrows == 0:
        print "---"
        print " No sources found. No output generated."
        print "---"
        sys.exit(1)
        
    outfile = args.outfile
    if args.outfile is '':
        logwrn("An empty name for output filename was given.")
        outfile = str(ra)+'_'+str(dec)+'_'+str(radius)+'.csv'
        logwrn("Filename for the output: %s" % outfile)
    logdbg("Output file %s",outfile)
    
    if outfile:
        table.write(outfile,format='ascii',delimiter=',')
    
    print "---"
    print " Table retrieved:"    
    table.pprint(max_width=-1)
    print "---"

    sys.exit()
    
