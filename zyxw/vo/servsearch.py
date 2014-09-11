#!/usr/bin/env python
#-*- coding:utf-8 -*-

from zyxw.io import log
logging = log.init()
logcrt = logging.critical
logerr = logging.error
logwrn = logging.warning
logdbg = logging.debug
loginf = logging.info

class CatalogValidator(object):

    # --- Auxiliary class ---
    class Table(object):
        def __init__(self):
            self._table = None
        def __nonzero__(self):
            return self._table != None
        def __len__(self):
            return len(self._table)
        def update(self,newTable):
            self._table = newTable
    # --- /Auxiliary class ---
    
    _nullPos = (0,0)
    _nullRad = 0.00001
    _ucds = []
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
        if isinstance(UCDs,list):
            self._ucds = UCDs[:]
        elif isinstance(UCDs,str):
            self._ucds = UCDs.split()
        else:
            raise TypeError("UCDs should be str or list")
        
    def setUnits(self,Units):
        if isinstance(Units,list):
            self._units = Units[:]
        elif isinstance(Units,str):
            self._units = Units.split()
        else:
            raise TypeError("UCDs should be str or list")
        
    def _checkUCDs(self):
        assert(self._table)
        ok = checkUCDs(self._table,self._ucds)
        if not ok:
            if not self._comments['isvalid']:
                self._comments['isvalid'] = []
            self._comments['isvalid'].append((ok,'UCDs do not match'))
        return ok
        
    def _checkUnits(self):
        assert(self._table)
        ok = checkUnits(self._table,self._units)
        if not ok:
            if not self._comments['isvalid']:
                self._comments['isvalid'] = []
            self._comments['isvalid'].append((ok,'Units do not match'))
        return ok
        
    def isValid(self):
        self.sync()
        return self._checkUCDs and self._checkUnits
        
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

def getUCD(tab):
    """Returns a list with all (valid) UCDs from a table"""
    from astropy.io.votable import ucd
    l1 = []
    for f in tab.fielddesc():
        if not f.ucd: continue
        l2 = []
        for u in ucd.parse_ucd(f.ucd):
            l2.append(str(u[1]))
        l1.extend(l2)
    return l1[:]

def checkUCDs(tab,UCDs=[]):
    """Returns a True if tab has one of the given UCDs; False otherwise"""
    if tab is None: return None
    l = getUCD(tab)
    ok = any( filter(lambda u:u in UCDs, set(l)) )
    return ok
    
def getUnit(tab):
    """Returns a list of units from a table"""
    l = []
    for f in tab.fielddesc():
        if not f.unit: continue
        l.append(str(f.unit).replace(' ',''))
    return l[:]

def checkUnits(tab,Units=[]):
    """Returns a True if tb has one of the given Units; False otherwise"""
    if tab is None: return None
    l = getUnit(tab)
    ok = any( filter(lambda u:u in Units, set(l)) )
    return ok
    
# --- /Auxiliary functions ---

import pyvo

def main(waveband,keyword='',service='conesearch',registry='US'):
    '''
    Search and filter services to be used for SED analysis
    '''
    
    ucds = ['em.X-ray','phot.flux','phot.flux.density','phot.count','phys.luminosity']
    units = ['ct/s','erg/s','erg/s/cm2','erg/s/cm^2','mW/m2','1e-17W/m2','ct/ks','mJy','ct','[10-7W]']

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
    catalogues = []
    cnt = 0
    _failed = []
    for r in records:
        cv = CatalogValidator(r)
        loginf("Retrieving table '%s'" % (cv.title()))
        cv.sync()
        if not cv:
            _failed.append(r)
            continue
        cv.setUCDs = ucds
        cv.setUnits = units
        catalogues.append(cv)
        cnt += 1
    loginf("%d tables were retrieved.")
    if len(_failed):
        _fn = [ f.title for f in _failed ]
        logwrn("%d tables were in a NULL state. They are: %s" % (len(_fn),_fn))
        del _fn
    del _failed
    
    cnt = 0
    for cv in catalogues:
        if cv.isValid():
            print cv.title()
            cnt += 1
    print("%d valid catalogues" % cnt)
    
if __name__ == '__main__':
    main('xray','index')
