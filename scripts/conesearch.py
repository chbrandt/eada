#!/usr/bin/env python
#-*- coding:utf-8 -*-

from zyxw.vo import conesearch as cs

import logging
import sys
import string
import warnings
warnings.simplefilter('ignore')

desc = """
    This script searchs for sources in a given position (RA,DEC) and radius (R) 
    in a given catalog. To see the available catalogs use the '--list' option.
"""

EXIT_OK     = 0
EXIT_ERROR  = 1
EXIT_EMPTY  = 10

def list_catalogs(cp):
    """List the available catalogs"""

    for k,d in cp.iteritems():
        print k
        for c,v in d.items():
            print "| %-10s : %s" % (c,v)
        print ""

def availableCatalogs(cp):
    """
    Get the names of the available catalogs
    """
    cats = [ k for k in cp.iterkeys() ]
    return cats
    
def setupParserOptions(parser,cp):
    """
    Define command line options
    """
    # Mutually exclusive options
    #  The options are meant to be "list" or "choose" catalogues or give the
    #  "url" directly.
    #
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument('--list', action='store_true',
                        help="Print the list os catalogs available for the search.")

    CATS = availableCatalogs(cp) if cp else []
    group.add_argument('--catalog', dest='cat', metavar='CATALOG',
                        choices = CATS,
                        help="Catalog to search for data. To see your choices use the '--list' option.")

    group.add_argument('--url', dest='url',
                        help="Service URL to query. To see some options use the '--list' option.")

    # (redundant) Group of options for better organize arguments
    #
    conesearch = parser.add_argument_group('Conesearch','Options for searching catalogues.')

    conesearch.add_argument('--ra', dest='ra', type=float, default=0,
                            help="Right Ascension of the object (in degrees by default)")

    conesearch.add_argument('--dec', dest='dec', type=float, default=0,
                            help="Declination of the object (in degrees by default)")

    conesearch.add_argument('--radius', type=float, dest='radius', default=0.00001,
                            help="Radius (around RA,DEC) to search for object(s)",)

    conesearch.add_argument('--runit', dest='runit', metavar='unit', default='degree',
                            choices=['degree','arcmin','arcsec'],
                            help="Unit for radius value. Choices are 'degree','arcmin','arcsec'.")

    # Output generation options
    #
    output = parser.add_argument_group('Output','Options for output generation.')
    output.add_argument('--columns', dest='cols', metavar='fieldname', nargs='*',
                        help="Columns to get from the retrieved catalog. The\
                         argument 'asdc' will output a preset of columns, suitable for ASDC.\
                         If not given, all columns will be output.")
    output.add_argument('--short', action='store_true',
                        help="Just outputs if at least one source was found.")
    output.add_argument('-o','--outfile', dest='outfile', nargs='?', const='', 
                        default=None, help="Filename to write the output, CSV format table file.")

    return parser

# --
def parseArguments(args,cp):
    
    from astropy import units
    
    ra = args.ra
    dec = args.dec
    logging.debug('RA:%s , DEC:%s', ra, dec)
    
    radius = args.radius
    ru = ''
    if args.runit == 'degree':
        ru = units.degree
    elif args.runit == 'arcmin':
        ru = units.arcmin
    elif args.runit == 'arcsec':
        ru = units.arcsec
    else:
        logging.error("Radius' unit is not valid. Use 'degree', 'arcmin' or 'arcsec'.")
        sys.exit(EXIT_ERROR)
        
    rad = radius*ru
    logging.debug('Radius %s', rad)
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
        logging.debug("Catalog (%s) url: %s", cat, url)
    else:
        url = args.url
        logging.debug("URL to search for sources: %s", url)

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
    logging.debug("Columns to output: %s", cols)

    return ra,dec,radius,url,cols


# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=desc)

    # DB/config input file
    #
    parser.add_argument('--db', dest='dbfile', metavar='filename', nargs='?',
                        help="DB/Config filename (ini file).")

    # Log
    #
    parser.add_argument('--log', nargs='?', const='conesearch.log', default=None,
                        help="Do *not* log the events of the script. By default all events are written to 'conesearch.log' file.")

    # --------------------------------------------------------------------------
    # Here we have a hack to read the content of the db file

    # Parse the known arguments
    args,unknown = parser.parse_known_args(sys.argv[:])

    # Start the logging
    if not args.log:
        logging.disable(logging.WARNING)
#        logging.basicConfig(format='[%(filename)s:%(funcName)20s] %(message)s',
#                            level=logging.INFO)
    else:
        logging.basicConfig(filename=args.log, filemode='w',
                            format='[%(filename)s:%(funcName)20s] %(message)s',
                            level=logging.NOTSET)

    # Read the db/config file
    import os
    from zyxw.io import config
    if args.dbfile:
        dbfile = os.path.abspath(args.dbfile)
    else:
        logging.warning("No DB file given. Using package's default.")
        import inspect
        dbfile = os.path.join(os.path.dirname(inspect.getfile(cs)), cs.CFGFILE)
        
    if os.path.exists(dbfile):
        cp = config.read_ini(dbfile)
    else:
        cp = None
    # --------------------------------------------------------------------------
    
    # Parse the arguments
    parser = setupParserOptions(parser,cp)
    args = parser.parse_args()
    
    if not (cp or args.url):
        parser.print_help()
        sys.exit(os.EX_IOERR)
        
    if args.list:
        list_catalogs(cp)
        sys.exit(os.EX_OK)

    # ---
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
        if not (args.cat or args.url):
            print(" Catalog/url not provided.")
            OK = False
        return OK
    # ---
    if not argumentsOK(args):
        sys.exit(EXIT_ERROR)
        
    # Parse the arguments
    ra,dec,radius,url,cols = parseArguments(args,cp)
    
    # Now, the main function does the search and columns filtering...
    table = cs.main(ra,dec,radius,url,cols)
    if table is None:
        if args.short:
            print "Failed"
        else:
            print "---"
            print "\033[91mNot able to access data for source in archive %s\033[0m" % (url)
            print "---"
        sys.exit(EXIT_ERROR)
    
    nrows = len(table)
    
    if args.short:
        print "Number of sources found %d" % nrows
        sys.exit(EXIT_OK)
    
    if nrows == 0:
        print "---"
        print "\033[91mNo sources found. No output generated.\033[0m"
        print "---"
        sys.exit(EXIT_EMPTY)
        
    outfile = args.outfile
    if args.outfile is '':
        logging.warning("An empty name for output filename was given.")
        outfile = str(ra)+'_'+str(dec)+'_'+str(radius)+'.csv'
        logging.warning("Filename for the output: %s" % outfile)
    logging.debug("Output file %s",outfile)
    
    if outfile:
        table.write(outfile,format='ascii',delimiter=',')
    
    print "---"
    print " Table retrieved:"    
    table.pprint(max_width=-1)
    print "---"

    sys.exit(EXIT_OK)
    