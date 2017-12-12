#!/usr/bin/env python
from __future__ import absolute_import
import sys
import timeout_decorator
TIMEOUT = 3

import string
from collections import OrderedDict as odict

from pyvo.dal.scs import SCSResults
from pyvo.dal.query import DALQueryError, DALServiceError

from . import metadata

import logging
logcrt = logging.critical
logerr = logging.error
logwrn = logging.warning
logdbg = logging.debug
loginf = logging.info


def _ustr(word):
    # return unicode(word).encode('utf-8')
    return str(word)


NULLPOS = (0,0)
NULLRAD = 0.0000001

# Wavebands available to search for catalogue data
# (for convenience I relate the UCD words used)
BANDS = {'radio'        : 'em.radio',
         'millimeter'   : 'em.mm',
         'mm'           : 'em.mm',
         'infrared'     : 'em.IR',
         'ir'           : 'em.IR',
         'optical'      : 'em.opt',
         'opt'          : 'em.opt',
         'ultraviolet'  : 'em.UV',
         'uv'           : 'em.UV',
         'xray'         : 'em.X-ray'}


def search(waveband, keyword='', ucds=[], units=[],
           service='conesearch', registry='US',
           sample=0, filter_columns=False,
           nprocs=1):
    '''
    Search and filter services to be used for SED analysis
    '''
    from pyvo import regsearch

    if not _validRegistry(registry):
        _regsOK = [k for k, v in _registries.items() if v]
        logcrt("Registry not supported. Choices are: %s" % (_regsOK))
        return False

    loginf("Querying registry '%s' for services '%s' providing '%s' data matching '%s' keyword"
            % (registry, service, waveband, keyword))

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

    catalogues = _selectCatalogs(records, ucds, units,
                                 filter_columns=filter_columns,
                                 nprocs=max(1,nprocs))

    loginf("%d tables were retrieved." % len(catalogues))

    return catalogues

main = search


class CatalogValidator(object):

    # --- Auxiliary class ---
    class Table(object):
        def __init__(self):
            self.clear()

        def __str__(self):
            return str(self.fields())

        def clear(self):
            self._pseudoTable = None
            self._votableTree = None
            self._originalTab = None

        def __bool__(self):
            return self._votableTree is not None

        def __len__(self):
            return len(self._table)

        def update(self, newTable):
            if newTable is not None and isinstance(newTable, SCSResults):
                self._pseudoTable = newTable
                self._votableTree = newTable.votable

        def fields(self):
            return self._votableTree.fields

        def fieldname_with_ucd(self, ucd):
            names = []
            for fld in self._pseudoTable.fieldnames:
                desc = self._pseudoTable.getdesc(fld)
                if desc.ucd and string.find(desc.ucd, ucd) >= 0:
                    names.append(fld)
            return names

        def fieldname_with_unit(self, unit):
            names = []
            for fld in self._pseudoTable.fieldnames:
                desc = self._pseudoTable.getdesc(fld)
                if desc.unit and string.find(str(desc.unit).replace(' ', ''), unit) >= 0:
                    names.append(fld)
            return names

    # --- /Auxiliary class ---

    def __init__(self, record):
        assert(record is not None)
        self._record = record
        self._table = self.Table()
        self._nullPos = NULLPOS
        self._nullRad = NULLRAD
        self._ucds = {}
        self._units = []
        self._columns = []

    def __bool__(self):
        assert(self._record)
        return bool(self._table)

    def __len__(self):
        assert(self._record)
        return len(self._table) if self._table is not None else 0

    @timeout_decorator.timeout(TIMEOUT)
    def _getTable(self):
        assert(self._record)
        import warnings
        warnings.filterwarnings('ignore')
        s = self._record.service
        try:
            r = s.search(pos=self._nullPos, radius=self._nullRad)
        except DALQueryError as e:
            r = None
        except DALServiceError as e:
            r = None
        except Exception as e:
            logging.error("Exception while querying service: {}".format(e))
            r = None
        return r

    def sync(self):
        if not self._table:
            try:
                t = self._getTable()
            except:
                t = None
            self._table.update(t)

    def setUCDs(self, UCDs):
        if UCDs is None:
            UCDs = []
        assert isinstance(UCDs, list)
        self._ucds = UCDs[:]

    def setUnits(self, Units):
        if Units is None:
            Units = []
        if isinstance(Units, list):
            self._units = Units[:]
        elif isinstance(Units, str):
            self._units = Units.split()
        else:
            raise TypeError("UCDs should be str or list")

    def _checkUCDs(self):
        assert self._table
        ok = True
        and_ucds = []
        for ucd in self._ucds:
            if isinstance(ucd, str):
                and_ucds.append(ucd)
                continue
            assert isinstance(ucd, list), '{}'.format(ucd)
            ok = ok and metadata.checkUCDs(self._table, ucd, True)
        if and_ucds:
            ok = ok and metadata.checkUCDs(self._table, and_ucds, True)
        return ok

    def _checkUnits(self):
        assert self._table
        ok = metadata.checkUnits(self._table, self._units)
        return ok

    def isValid(self):
        self.sync()
        ok1 = self._checkUCDs()
        ok2 = self._checkUnits()
        return ok1 and ok2

    def filterColumns(self):
        self.sync()
        ucds = []
        for ucd in self._ucds:
            if isinstance(ucd, str):
                ucds.append(ucd)
                continue
            assert isinstance(ucd, list)
            ucds.extend(ucd)
        nameCols = metadata.matchUCDs(self._table, ucds, True)
        units = self._units
        nameCols.extend(metadata.matchUnits(self._table, units, True))
        _set = set(nameCols)
        nameCols = list(_set)
        for field in self._table.fields():
            for name in nameCols:
                if field.name is name:
                    ucd = field.ucd
                    unit = field.unit
                    descr = field.description
                    self._columns.append((name, ucd, unit, descr))

    def useAllColumns(self):
        self.sync()
        for field in self._table.fields():
            name = field.name
            ucd = str(field.ucd)
            unit = str(field.unit)#.to_string())
            descr = field.description
            self._columns.append( (name,ucd,unit,descr) )

    def summary(self):
        out = odict()
        out['title']        = self.title()
        out['url']          = self.url()
        out['ivoid']        = self.ivoid()
        out['creators']     = self.publisher()
        out['description']  = self.description()
        out['columns'] = [ col[0] for col in self._columns ]
        out['ucds']  = [ col[1] for col in self._columns ]
        out['units'] = [ col[2] for col in self._columns ]
        out['descriptions'] = [ col[3] for col in self._columns ]
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
        _sn = self._record.short_name
        _sn = '_'.join(_sn.split())  # or 'EMPTY'
        # return ''.join(filter(str.isalnum,str(_sn)))
        return _sn

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

def _selectCatalog(record,ucds=None,units=None,filter_columns=False):
    cv = CatalogValidator(record)

    loginf("Retrieving table '%s'" % (cv.title()))
    cv.sync()

    if not cv:
        return None

    cv.setUCDs(ucds)
    cv.setUnits(units)

    if not cv.isValid():
        return False

    if filter_columns:
        cv.filterColumns()
    else:
        cv.useAllColumns()

    return cv

select_catalog = _selectCatalog


def _selectCatalogs(records,ucds=None,units=None,filter_columns=False,nprocs=1):
    '''
    '''
    def printProgress(_progress):
        i = _progress[0][0]
        n = _progress[1][0]
        # s = _progress[2][0]
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

        cv = _selectCatalog(r,ucds=ucds,units=units,filter_columns=filter_columns)
        if cv is None:
            _failed.append(r)
            # _progress[2][0] += 'x'
            continue
        if cv is False:
            _unwanted.append(cv)
            # _progress[2][0] += '-'
            continue
        catalogues.append(cv)

        # _progress[2][0] += 'o'
        cnt += 1

    printProgress(_progress)
    print()
    assert(len(catalogues)+len(_failed)+len(_unwanted)==len(records))

    if len(_failed):
        _fn = [ f.res_title for f in _failed ]
        logwrn("%d tables were in a NULL state. They are:\n%s" %
                ( len(_fn), '\n'.join(_fn) ))
        del _fn
    del _failed

    return catalogues
