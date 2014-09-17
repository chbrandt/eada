#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

import logging
logcrt = logging.critical
logerr = logging.error
logwrn = logging.warning
logdbg = logging.debug
loginf = logging.info

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
            
    # --- /Auxiliary class ---
    
    _nullPos = (0,0)
    _nullRad = 0.00001
    _ucds = {}
    _units = []
    
    def __init__(self,record):
        assert(record != None)
        self._record = record
        self._table = self.Table()
        
    def __nonzero__(self):
        assert(self._record)
        return bool(self._table)
        
    def __len__(self):
        assert(self._record)
        return len(self._table) if self._table != None else 0
        
    def _getTable(self):
        assert(self._record)
        import warnings; warnings.filterwarnings('ignore')
        s = self._record.to_service()
        return s.search(pos=self._nullPos, radius=self._nullRad)
        
    def sync(self):
        if not(self._table):
            try:
                t = self._getTable()
            except:
                return
            self._table.update(t)
        assert(self._table)
        
    def setUCDs(self,UCDs):
        assert(isinstance(UCDs,dict))
        self._ucds = UCDs.copy()
        
    def setUnits(self,Units):
        if isinstance(Units,list):
            self._units = Units[:]
        elif isinstance(Units,str):
            self._units = Units.split()
        else:
            raise TypeError("UCDs should be str or list")
        
    def _checkUCDs(self):
        assert(self._table)
        emUCD = self._ucds.keys()
        assert(len(emUCD)==1)
        ok1 = metadata.checkUCDs(self._table,emUCD,True)
        ok2 = metadata.checkUCDs(self._table,self._ucds[emUCD[0]],True)
        return ok1 and ok2
        
    def _checkUnits(self):
        assert(self._table)
        ok = metadata.checkUnits(self._table,self._units)
        return ok
        
    def isValid(self):
        self.sync()
        ok1 = self._checkUCDs()
        ok2 = self._checkUnits()
        return ok1 and ok2
        
    def summary(self):
        out= {}
        out['description']  = self.description()
        out['url']          = self.url()
        out['title']        = self.title()
        out['publisher']    = self.publisher()
        out['ivoid']        = self.ivoid()
        return out.copy()
        
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

def selectCatalogs(records,ucds,units):
    '''
    '''
    def printProgress(_progress):
        i = _progress[0][0]
        n = _progress[1][0]
        s = _progress[2][0]
        prog = int(100*float(i)/n)
        sys.stdout.write("\r[%d%% - %d/%d] %s" % (prog,i,n,s))
        sys.stdout.flush()
        
    catalogues = []
    cnt = 0
    _failed = []
    _unwanted = []
    _progress = ([0],[0],[''])
    for i,r in enumerate(records):
        _progress[0][0] = i+1
        _progress[1][0] = records.nrecs
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
        catalogues.append(cv)
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

# --- /Auxiliary functions ---

import pyvo

def main(waveband, keyword='', ucds={}, units=[],
         service='conesearch', registry='US'):
    '''
    Search and filter services to be used for SED analysis
    '''
    
    if not _validRegistry(registry):
        _regsOK = [ k for k,v in _registries.items() if v ]
        logcrt("Registry not supported. Choices are: %s" % (_regsOK))
        return False
    
    loginf("Querying registry '%s' for services '%s' providing '%s' data matching '%s' keyword" 
            % (registry,service,waveband,keyword))
            
    # We use PyVO for querying the registry
    records = pyvo.regsearch(waveband=waveband,
                             keywords=keyword,
                             servicetype=service)
    loginf("Number of services found: %d" % (records.nrecs))
    
    # Let's get --first-- empty tables from the retrieved records/services
    catalogues = selectCatalogs(records,ucds,units)
    loginf("%d tables were retrieved." % len(catalogues))

    return catalogues
    
