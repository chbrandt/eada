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

# Wavebands available to search for catalogue data
# (for convenience I relate the UCD words used)
BANDS = {'radio'        : 'em.radio',
         'millimeter'   : 'em.mm',
         'infrared'     : 'em.IR',
         'optical'      : 'em.opt',
         'uv'           : 'em.UV',
         'xray'         : 'em.X-ray'}

from pyvo.dal.scs import SCSResults
from pyvo.dal.query import DALQueryError,DALServiceError

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

        def fields(self):
            return self._votableTree.fields

        def fieldname_with_ucd(self,ucd):
            names = []
            for fld in self._pseudoTable.fieldnames:
                desc = self._pseudoTable.getdesc(fld)
                if desc.ucd and string.find(desc.ucd,ucd) >= 0:
                    names.append(fld)
            return names

        def fieldname_with_unit(self,unit):
            names = []
            for fld in self._pseudoTable.fieldnames:
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
        self._nullRad = 0.000001
        self._ucds = {}
        self._units = []
        self._columns = []

    def __nonzero__(self):
        assert(self._record)
        return bool(self._table)

    def __len__(self):
        assert(self._record)
        return len(self._table) if self._table != None else 0

    def _getTable(self):
        assert(self._record)
        import warnings; warnings.filterwarnings('ignore')
        s = self._record.service
        try:
            r = s.search(pos=self._nullPos, radius=self._nullRad)
        except DALQueryError as e:
            r = None
        except DALServiceError as e:
            r = None
        except Exception as e:
            logging.error("Exception while querying service: {}".format(e))
        return r

    def sync(self):
        if not self._table:
            t = self._getTable()
            self._table.update(t)

    def setUCDs(self,UCDs):
        if UCDs is None:
            UCDs = []
        assert isinstance(UCDs,list)
        self._ucds = UCDs[:]

    def setUnits(self,Units):
        if Units is None:
            Units = []
        if isinstance(Units,list):
            self._units = Units[:]
        elif isinstance(Units,str):
            self._units = Units.split()
        else:
            raise TypeError("UCDs should be str or list")

    def _checkUCDs(self):
        assert self._table
        ok = True
        and_ucds = []
        for ucd in self._ucds:
            if isinstance(ucd,str):
                and_ucds.append(ucd)
                continue
            assert isinstance(ucd,list), '{}'.format(ucd)
            ok *= metadata.checkUCDs(self._table,ucd,True)
        if and_ucds:
            ok *= metadata.checkUCDs(self._table,and_ucds,True)
        # emUCD = self._ucds.keys()
        # assert(len(emUCD)==1)
        # ok1 = metadata.checkUCDs(self._table,emUCD,True)
        # ok2 = metadata.checkUCDs(self._table,self._ucds[emUCD[0]],True)
        # return ok1 and ok2
        return ok

    def _checkUnits(self):
        assert self._table
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
        ucds = []
        for ucd in self._ucds:
            if isinstance(ucd,str):
                ucds.append(ucd)
                continue
            assert isinstance(ucd,list)
            ucds.extend(ucd)
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
                    descr = field.description
                    self._columns.append( (name,ucd,unit,descr) )

    def useAllColumns(self):
        self.sync()
        for field in self._table.fields():
            name = field.name
            ucd = field.ucd
            unit = field.unit
            descr = field.description
            self._columns.append( (name,ucd,unit,descr) )

    def summary(self):
        out = odict()
        out['title']        = self.title()
        out['url']          = self.url()
        out['ivoid']        = self.ivoid()
        out['creators']     = self.publisher()
        out['description']  = self.description()
        out['columns_name'] = [ _ustr(col[0]) for col in self._columns ]
        out['columns_ucd']  = [ _ustr(col[1]) for col in self._columns ]
        out['columns_unit'] = [ _ustr(col[2]) for col in self._columns ]
        out['columns_desc'] = [ _ustr(col[3]) for col in self._columns ]
        return out

    def description(self):
        return self._record.res_description

    def url(self):
        return self._record.access_url

    def title(self):
        return self._record.res_title

    def publisher(self):
        return self._record.creators

    def ivoid(self):
        return self._record.ivoid

    def shortname(self):
        _sn = self._record.short_name.split()[0]
        return filter(str.isalnum,str(_sn))

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

def selectCatalogs(records,ucds=None,units=None,filter_columns=False):
    '''
    '''
    def printProgress(_progress):
        i = _progress[0][0]
        n = _progress[1][0]
        s = _progress[2][0]
        prog = int(100*float(i)/n)
        # sys.stdout.write("\r[%d%% - %d/%d] %s" % (prog,i,n,s))
        sys.stdout.write("\r[%d%% - %d/%d]" % (prog,i,n))
        sys.stdout.flush()

    catalogues = []
    cnt = 0
    _failed = []
    _unwanted = []
    _progress = ([0],[0],[''])
    for i,r in enumerate(records):
        _progress[0][0] = i+1
        _progress[1][0] = len(records)
        printProgress(_progress)

        cv = CatalogValidator(r)
        loginf("Retrieving table '%s'" % (cv.title()))
        cv.sync()

        if not cv:
            _failed.append(r)
            _progress[2][0] += 'x'
            continue

        cv.setUCDs(ucds)
        cv.setUnits(units)

        if not cv.isValid():
            _unwanted.append(cv)
            _progress[2][0] += '-'
            continue

        if filter_columns:
            cv.filterColumns()
        else:
            cv.useAllColumns()
        catalogues.append(cv)

        _progress[2][0] += 'o'
        cnt += 1

    printProgress(_progress)
    print('\n')
    assert(len(catalogues)+len(_failed)+len(_unwanted)==len(records))

    if len(_failed):
        _fn = [ f.res_title for f in _failed ]
        logwrn("%d tables were in a NULL state. They are:\n%s" %
                ( len(_fn), '\n'.join(_fn) ))
        del _fn
    del _failed

    return catalogues


def search(waveband, keyword='', ucds=[], units=[],
            service='conesearch', registry='US',
            sample=0, filter_columns=False,
            parallel=False):
    '''
    Search and filter services to be used for SED analysis
    '''
    from pyvo import regsearch

    if not _validRegistry(registry):
        _regsOK = [ k for k,v in _registries.items() if v ]
        logcrt("Registry not supported. Choices are: %s" % (_regsOK))
        return False

    loginf("Querying registry '%s' for services '%s' providing '%s' data matching '%s' keyword"
            % (registry,service,waveband,keyword))

    # We use PyVO for querying the registry
    records = regsearch(waveband=waveband,
                         keywords=keyword,
                         servicetype=service)
    num_records = len(records)
    loginf("Number of services found: %d" % (num_records))

    if not num_records:
        print("No catalogues found.")
        return None

    if sample is True:
        sample = int(num_records/10)
    if sample:
        assert sample > 0, "Sample should be a positive number"
        sample = int(sample) if sample >= 1 else int(num_records*sample)
        from random import shuffle
        irec = list(range(num_records))
        shuffle(irec)
        records = [ records[i] for i in irec[:sample] ]

    if parallel:
        def spawn(f):
            def fun(pipe,x):
                pipe.send(f(x))
                pipe.close()
            return fun
        def parmap(f,x):
            from itertools import izip
            from multiprocessing import Process,Pipe
            pipe=[ Pipe() for _ in x ]
            proc=[Process(target=spawn(f),args=(c,x)) for x,(p,c) in izip(x,pipe)]
            [ p.start() for p in proc ]
            [ p.join() for p in proc ]
            return [ p.recv() for (p,c) in pipe ]
        foo = lambda r: selectCatalogs(r,ucds,units)
        catalogues = parmap(foo, records)
    else:
        catalogues = selectCatalogs(records,ucds,units,
                                    filter_columns=filter_columns)
    loginf("%d tables were retrieved." % len(catalogues))

    return catalogues

main = search
