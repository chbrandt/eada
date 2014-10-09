# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 15:59:21 2014

@author: chbrandt
"""

import json
import string
import re

from collections import OrderedDict

from astropy.io.votable import ucd
from astropy.table import Table

from zyxw.vo.conesearch import conesearch

import warnings
warnings.simplefilter('ignore')

class UCDs(ucd.UCDWords):
    '''Define a function to return the list of UCD words currently in use'''
    def words(self,prefix=None):
        vals = self._capitalization.values()
        if prefix:
            assert(prefix in self._capitalization.keys())
            vals = [ str(w) for w in vals if string.find(w,prefix)==0 ]
        vals.sort()
        return vals

def getUCD(SCSresult):
    """Returns a list with all (valid) UCDs from a table"""
    from astropy.io.votable import ucd
    tab = SCSresult
    l1 = []
    for f in tab.fielddesc():
        if not f.ucd:
            continue
        if not ucd.check_ucd(f.ucd):
            continue
        l2 = []
        for u in ucd.parse_ucd(f.ucd):
            _u = str(u[1])
            if not _u in l1:
                l2.append(_u)
        l1.extend(l2)
    return l1

def isAlpha(s):
    if s.isalpha() or s is '-':
        return True
    return False

# Wavebands found on USVAO conesearch services. Values were collected from
#  the JSON files created by Astropy's function 'check_conesearch_sites'.
WAVEBANDS = ['EUV',
             'Gamma-ray',
             'Infrared',
             'Optical',
             'Radio',
             'UV',
             'X-ray']
             
    
def main(jsonFilename):
    '''
    The JSON file given is the output from Astropy's validate service tool.
    The file contains a set of metadata which we are interested in. The aim 
    of this function is to read these data and build a (csv) file/table.
    '''
    
    # First, open the json file
    try:
        fp = open(jsonFilename)
        jfile = json.load(fp)
        catalogs = jfile['catalogs']
    except:
        return False
        
    # Information will be stored here, at 'mdata'
    mdata = OrderedDict()
    # add an entrance for the service/catalog name
    mdata['name'] = []
    # entrances for the supported wavebands
    for wb in WAVEBANDS:
        mdata[wb] = []
    # and entrances for the related UCDs
    ucds = UCDs()
    for uw in ucds.words():
        mdata[uw] = []

    mdata['unknown'] = []

    # Now, let's run over each catalog entry and get the data    
    for name,cat in catalogs.iteritems():
        # create a temporary box for the current catalog's metadata
        md = {}

        # the name
        md['name'] = str(name)
        
        # the waveband; first, (null) initialize the entry
        for wb in WAVEBANDS:
            md[wb] = False
        # ..and now, read it, clean and store
        s = re.sub('"','',str(cat['waveband']))
        wband = ''
        for _ in s:
            wband += _ if isAlpha(_) else ','
        wband = wband.split(',')
        wband = [ w for w in wband if w ]
        unknown_wb = ''
        for wb in wband:
            if md.has_key(wb):
                md[wb] = True
            else:
                unknown_wb = unknown_wb+','+wb if unknown_wb else wb
            
        # The UCDs
        for uw in ucds.words():
            md[uw] = False
        url = str(cat['url'])
        try:
            print("Searching %s" % (cat['title']))
            res = conesearch(0,0,0.0001,url)
        except:
            continue
        if res is None:
            continue
        resUCDs = getUCD(res)
        unknown_ucd = ''
        for uw in resUCDs:
            if md.has_key(uw):
                md[uw] = True
            else:
                unknown_ucd = unknown_ucd+','+uw if unknown_ucd else uw
            
        for k in md.keys():
            mdata[k].append(md[k])
        unknown = '#waveband:'+','+unknown_wb
        unknown += '#ucd:'+','+unknown_ucd
        mdata['unknown'].append(unknown)

    tab = Table(mdata)
    tab.pprint()
    return tab
#    for k in mdata.keys():
#        for v in mdata[k]:
#            print v,
#        print "\n"
