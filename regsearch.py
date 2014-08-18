#!/usr/bin/env python
#

# This code is meant to deal with the search of data using the VO framework and basically
#  filtering it.

from pyvo import regsearch

# TODO: get the parameters from the user. Here called ST, WB, KW.
ST = 'conesearch'
WB = 'xray'
KW = 'index'
servResults = regsearch( servicetype=ST, waveband=WB, keywords=KW )

# TODO: present the list of resources found, with their metadata

# TODO: set filters to select data based on resource's metadata
UCD=['em.X-ray','phot.flux','phot.flux.density','phot.count','phys.luminosity']
UNT=['ct/s','erg/s','erg/s/cm2']

class serviceAvail:
    def __init__(self,service):
        assert(service)
        self._service = service
        self._table = None
        self._enable = True
        
    def isEnabled(self):
        return self._enable
        
    def setEnable(self,status=True):
        self._enable = status
        
    def setTable(self,tab):
        self._table = tab
        
    def table(self):
        return self._table
        
    def search(self,pos=(0,0),radius=0.00001):
        assert(self._service)
        q = self._service.to_service()
        try:
            t = q.search(pos=pos,radius=radius)
        except:
            t = None
        return t
        
def servicesMetadata(services):
    assert(services)
    servicesAvail = {}
    for _s in services:
        sA = serviceAvail(_s)
        tab = sA.search()
        if tab:
            sA.setTable(tab)
            servicesAvail[_s] = sA
    return servicesAvail
    
class RegSearch(object):
    """
    Search for services on registry
    """
    _options = {'type' : ['conesearch'],
                'band' : ['xray']
                }
    
    def __init__(self):
        self._servicetype = None
        self._waveband = None
        self._keywords = None
        self._servicesAvail = None
    
    def setService(self,type):
        if type in self._options['type']:
            self._servicetype = type
        else:
            raise ValueError("Given type is not available")
    
    def setWaveband(self,band):
        if band in self._options['band']:
            self._waveband = band
        else:
            raise ValueError("Given band is not available")
    
    def setKeyword(self,word):
        if isinstance(word,str):
            self._keywords = word
        else:
            raise TypeError("Given word is not compatible")
    
    def search(self):
        serviceResults = regsearch( servicetype=self._servicetype,
                                    waveband = self._waveband,
                                    keywords = self._keywords)
        if serviceResults:
            mTab = servicesMetadata(serviceResults)
            self._servicesAvail = mTab
    
    def filterUCD(self,args=[],neg=False):
        if self._serviceAvail is None:
            return False
        for serv,struc in self._serviceAvail.items():
            if neg:
                struc.setEnable(not checkUCD(struc.table(),args))
            else:
                struc.setEnable(checkUCD(struc.table(),args))
        
    def filterUnits(self,args=[],neg=False):
        if self._serviceAvail is None:
            return False
        for serv,struc in self._serviceAvail.items():
            if neg:
                struc.setEnable(not checkUnit(struc.table(),args))
            else:
                struc.setEnable(checkUnit(struc.table(),args))
        
    def filterDescription(self,pattern,neg=False):
        import re
        if self._serviceAvail is None:
            return False
        reobj = re.compile(pattern)
        for serv,struc in self._serviceAvail.items():
            desc = serv.description
            struc.setEnable(not reobj.search(desc) is None)
        
        
def checkUCD(votable,ucds):
    from astropy.io.votable import ucd
    t = votable
    tucds = set()
    for f in t.fielddesc():
        fucds = set([ str(u) for u in ucd.parse_ucd(f.ucd) ])
        tucds.update(fucds)
    return any( filter(lambda u: u in ucds, tucds) )

def checkUnit(votable,units):
    from astropy import units
    t = votable
    tunt = set()
    for f in t.fielddesc():
        funt = set([ set(u) for u in f.unit ])
        tunt.update(funt)
    return any( filter(lambda u: u in units, tunt) )

