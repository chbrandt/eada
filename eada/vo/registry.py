#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

import logging
logcrt = logging.critical
logerr = logging.error
logwrn = logging.warning
logdbg = logging.debug
loginf = logging.info

import string

from collections import OrderedDict as odict

def _ustr(word):
    return unicode(word).encode('utf-8')

import metadata

def search(waveband, keywords='', ucds=None, units=None,
         service='conesearch'):
    '''
    Search and filter services to be used for SED analysis
    '''
    from pyvo import regsearch

    registry='US'
    if not _validRegistry(registry):
        _regsOK = [ k for k,v in _registries.items() if v ]
        logcrt("Registry not supported. Choices are: %s" % (_regsOK))
        return False

    loginf("Querying registry '%s' for services '%s' providing '%s' data matching '%s' keyword"
            % (registry,service,waveband,keywords))

    # We use PyVO for querying the registry
    records = regsearch(waveband=waveband,
                         keywords=keywords,
                         servicetype=service)
    loginf("Number of services found: %d" % (records.nrecs))

    # Let's get --first-- empty tables from the retrieved records/services
    if ucds is None:
        ucds = _ucds
    if units is None:
        units = _units
    catalogues = select_catalogs(records,ucds,units)
    loginf("%d tables were retrieved." % len(catalogues))

    return catalogues

_ucds = ['pos.eq',
        'POS_EQ_RA_MAIN',
        'POS_EQ_DEC_MAIN',
        'phot.mag',
        'phot.count',
        'phys.luminosity',
        'phot.flux']

_units = ['h:m:s',
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

# Wavebands available to search for catalogue data
# (for convenience I relate the UCD words used)
BANDS = {'radio'        : 'em.radio',
         'millimeter'   : 'em.mm',
         'infrared'     : 'em.IR',
         'optical'      : 'em.opt',
         'uv'           : 'em.UV',
         'xray'         : 'em.X-ray'}

from pyvo.dal.scs import SCSResults
import os
from eada.io import config

class Aux:
    @staticmethod
    def writeCatalogs(catalogList,at=''):
        """
        Write down INI (config) file for catalogues (resources)
        """
        catalogues = catalogList
        assert isinstance(catalogues,list)

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
            assert isinstance(c,CatalogValidator)
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


class CatalogValidatorList(object):
    def __init__(self):
        self.lst = list()

    def append(self,value):
        self.lst.append(value)

    def __len__(self):
        return len(self.lst)

    def write(self,at=''):
        Aux.writeCatalogs(self.lst,at)

class CatalogValidator(object):

    # --- Auxiliary class ---
    class Table(object):
        def __init__(self):
            self.clear()

        def clear(self):
            self._pseudoTable = None
            self._votableTree = None
            self._originalTab = None

        def __nonzero__(self):
            return self._votableTree != None

        def __len__(self):
            return len(self._table)

        def update(self,newTable):
            if newTable != None and isinstance(newTable,SCSResults):
                self._pseudoTable = newTable
                self._votableTree = newTable.votable
            else:
                raise(TypeError,"Instance of SCSResults expected.")

        def fields(self):
            return self._votableTree.fields

        def fieldname_with_ucd(self,ucd):
            names = []
            for fld in self._pseudoTable.fieldnames():
                desc = self._pseudoTable.getdesc(fld)
                if desc.ucd and string.find(desc.ucd,ucd) >= 0:
                    names.append(fld)
            return names

        def fieldname_with_unit(self,unit):
            names = []
            for fld in self._pseudoTable.fieldnames():
                desc = self._pseudoTable.getdesc(fld)
                if desc.unit and string.find(str(desc.unit).replace(' ',''),unit) >= 0:
                    names.append(fld)
            return names

    # --- /Auxiliary class ---

    def __init__(self,record):
        assert(record != None)
        self._record = record
        self._table = self.Table()
        self._nullPos = (0,0)
        self._nullRad = 1e-15
        # self._ucds = {}
        self._ucds = []
        self._units = []
        self._columns = []

    def __nonzero__(self):
        assert(self._record)
        return bool(self._table)

    def __len__(self):
        assert(self._record)
        return len(self._table) if self._table != None else 0

    def _getTable(self):
        print "getting table"
        import socket
        socket.setdefaulttimeout(5)
        assert(self._record)
        import warnings; warnings.filterwarnings('ignore')
        s = self._record.to_service()
        return s.search(pos=self._nullPos, radius=self._nullRad)

    def sync(self):
        if not(self._table):
            print "sync: not table"
            try:
                t = self._getTable()
                print "sync: getting table"
            except:
                print "sync: try-excepted"
                return
            self._table.update(t)
        assert(self._table)

    def setUCDs(self,UCDs):
        # assert(isinstance(UCDs,dict))
        # self._ucds = UCDs.copy()
        assert isinstance(UCDs,list)
        self._ucds = UCDs[:]

    def setUnits(self,Units):
        if isinstance(Units,list):
            self._units = Units[:]
        elif isinstance(Units,str):
            self._units = Units.split()
        else:
            raise TypeError("UCDs should be str or list")

    def _checkUCDs(self):
        assert(self._table)
        # emUCD = self._ucds.keys()
        # assert(len(emUCD)==1)
        # ok1 = metadata.checkUCDs(self._table,emUCD,True)
        # ok2 = metadata.checkUCDs(self._table,self._ucds[emUCD[0]],True)
        # return ok1 and ok2
        return metadata.checkUCDs(self._table,self._ucds,True)

    def _checkUnits(self):
        assert(self._table)
        ok = metadata.checkUnits(self._table,self._units)
        return ok

    def isValid(self):
        self.sync()
        ok1 = self._checkUCDs()
        ok2 = self._checkUnits()
        return ok1 and ok2

    def filterColumns(self):
        self.sync()

        # ucds = self._ucds.keys()
        # assert(len(ucds)==1)
        # ucds.extend(self._ucds[ucds[0]])
        ucds = self._ucds[:]

        nameCols = metadata.matchUCDs(self._table,ucds,True)
        units = self._units
        nameCols.extend(metadata.matchUnits(self._table,units,True))
        _set = set(nameCols)
        nameCols = list(_set)
        for field in self._table.fields():
            for name in nameCols:
                if field.name is name:
                    ucd = field.ucd
                    unit = field.unit
                    self._columns.append( (name,ucd,unit) )

    def summary(self):
        out = odict()
        out['title']        = self.title()
        out['url']          = self.url()
        out['ivoid']        = self.ivoid()
        out['publisher']    = self.publisher()
        out['description']  = self.description()
        out['columns_name'] = [ _ustr(col[0]) for col in self._columns ]
        out['columns_ucd']  = [ _ustr(col[1]) for col in self._columns ]
        out['columns_unit'] = [ _ustr(col[2]) for col in self._columns ]
        return out

    def description(self):
        return self._record.get('description')

    def url(self):
        return self._record.accessurl

    def title(self):
        return self._record.title

    def publisher(self):
        return self._record.publisher

    def ivoid(self):
        return self._record.ivoid

    def shortname(self):
        _sn = self._record.shortname.split()[0]
        return filter(str.isalnum,_sn)

    def fielddesc(self):
        fl = []
        for f in self._table.fields():
            fl.append([f.name,f.description,f.ucd,f.unit])
        return fl


# --- Auxiliary functions ---

#TODO: so far pyvo supports only access to USVAO registry.
_registries = { 'US' : 1,
                'EU' : 0
              }
def _validRegistry(ID):
    '''
    Check whether given registry is of this code's knowledge

    * So far is a dumb function, since pyvo supports only USVAo registry!
    '''
    return bool(_registries[ID])


def _retrieveTable(record):
    '''
    Retrieve an empty table referenced by the record
    '''
    serv = record.to_service()
    logdbg("Table being accessed at '%'" % (serv.baseurl))
    tab = serv.search( pos=(0,0), radius=0.00001 )
    logdbg("Qyeried URL: '%s'" % (tab.queryurl))
    return tab


def select_catalogs(records,ucds,units):
    """
    From the list of 'records', select those matching 'ucds' and 'units'

    Output:
    - list of `~CatalogValidator`

    """
    def printProgress(_progress):
        i = _progress[0][0]
        n = _progress[1][0]
        s = _progress[2][0]
        prog = int(100*float(i)/n)
        sys.stdout.write("\r[%d%% - %d/%d] %s" % (prog,i,n,s))
        sys.stdout.flush()

    catalogues = CatalogValidatorList()
    cnt = 0
    _failed = []
    _unwanted = []
    _progress = ([0],[0],[''])
    for i,r in enumerate(records):
        _progress[0][0] = i+1
        _progress[1][0] = records.nrecs
        printProgress(_progress)
        cv = CatalogValidator(r)
        print "CatalogValidator instanciated"
        loginf("Retrieving table '%s'" % (cv.title()))
        cv.sync()
        print "CV synched"
        if not cv:
            _failed.append(r)
            _progress[2][0] += 'x'
            print "FAILED"
            continue
        cv.setUCDs(ucds)
        print "UCDs set -- ",ucds
        cv.setUnits(units)
        print "Units set -- ",units
        if not cv.isValid():
            _unwanted.append(cv)
            _progress[2][0] += '-'
            print "INVALID"
            continue
        cv.filterColumns()
        print "CV cols filtered"
        catalogues.append(cv)
        print "CV appended"
        _progress[2][0] += 'o'
        cnt += 1

    printProgress(_progress)
    print('\n')
    assert(len(catalogues)+len(_failed)+len(_unwanted)==records.nrecs)

    if len(_failed):
        _fn = [ f.title for f in _failed ]
        logwrn("%d tables were in a NULL state. They are:\n%s" %
                ( len(_fn), '\n'.join(_fn) ))
        del _fn
    del _failed

    return catalogues
