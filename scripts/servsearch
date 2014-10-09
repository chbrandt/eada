#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 11:09:47 2014

@author: chbrandt
"""

ucds = ['pos.eq',
        'POS_EQ_RA_MAIN',
        'POS_EQ_DEC_MAIN',
        'phot.mag',
        'phot.count',
        'phys.luminosity',
        'phot.flux']

units = ['h:m:s',
         'd:m:s',
         'ct/s',
         'erg/s',
         'erg/s/cm2',
         'erg/s/cm^2',
         'mag',
         'mW/m2',
         '1e-17W/m2',
         'ct/ks',
         'mJy',
         'ct',
         '[10-7W]']

desc = """
    Code to search (USVAO) registry for catalogue services.
    It is hardcoded to look for catalogues providing spectral emission data;
    the columns/fields should present (any of) the following UCDs and units, resp:

    UCDs: %s
    Units: %s
    """ % (ucds,units)

import sys
import os

from zyxw.vo import servsearch
from zyxw.io import config

import logging
LOGLEVEL = logging.DEBUG

def writeCatalogs(catalogues,at=''):
    localDir = './'
    if not at:
        at = localDir
    if not (os.path.exists(at) or at is localDir):
        try:
            os.mkdir(at)
        except:
            print >> sys.stderr, "Not able to create directory '%s'. Check your permissions." % at
            sys.exit(1)
    
    try:
        fp = open(at+'/README.txt','w')
    except:
        print >> sys.stderr, "Not able to write to directory '%s'. Check your permissions." % at
    
    print("\nCatologues selected [%d]:" % len(catalogues))
    out = {}
    for c in catalogues:
        out[c.shortname()] = c.summary()
        if False:
            with open(at+'/'+c.shortname()+'.txt','w') as fp:
                for f in c.fielddesc():
                    f0 = unicode(f[0]).enconde('utf-8')
                    f1 = unicode(f[1]).enconde('utf-8')
                    f2 = unicode(f[2]).enconde('utf-8')
                    f3 = unicode(f[3]).enconde('utf-8')
                    fp.write("%-20s : %-40s : %-35s : %-10s\n" % (f0,f1,f2,f3))
    config.write_ini(out,at+'/CATALOGS.ini')
    
# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('band', metavar='waveband',
                        choices=servsearch.BANDS.keys(),
                        help='Waveband of interest to search for.')
                        
    parser.add_argument('--keywords', nargs='?', action='store',
                        help='Special keywords to be found at catalogues.')
                        
    # Log
    #
    parser.add_argument('--log', nargs='?', const='servsearch.log', default=None,
                        help="Log script steps. A filename can be given as argument.")

    # Parse the known arguments
    args,unknown = parser.parse_known_args()

    # Start the logging
    if args.log:
        logging.basicConfig(filename=args.log, filemode='w',
                            format='[%(filename)s:%(funcName)20s] %(message)s',
                            level=LOGLEVEL)
    else:
        logging.disable(logging.NOTSET)

    _ucd = servsearch.BANDS[args.band]
    ucds = {_ucd:ucds}
    
    # Run
    catalogues = servsearch.main(args.band, args.keywords, ucds, units)
    
    writeCatalogs(catalogues,args.band)
    
