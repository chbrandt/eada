# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 17:04:01 2014

@author: chbrandt
"""

def getUCD(tab):
    """Returns a list with all (valid) UCDs from a table"""
    from astropy.io.votable import ucd
    l1 = []
    for f in tab.fields():
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

def matchUCDs(tab,UCDs=[],substring=False):
    """Returns a list with the matching UCDs"""
    if tab is None:
        return []
    names = []
    for u in UCDs:
        names.extend(tab.fieldname_with_ucd(u))
    ns = set(names)
    return list(ns)

def matchUnits(tab,units=[],substring=False):
    """Returns a list with the matching UCDs"""
    if tab is None:
        return []
    names = []
    for u in units:
        names.extend(tab.fieldname_with_unit(u))
    ns = set(names)
    return list(ns)

def checkUCDs(tab,UCDs=[],substring=False):
    """Returns a True if tab has one of the given UCDs; False otherwise"""
    if tab is None:
        return False
    if not UCDs:
        return True
    import string
    l = getUCD(tab)
    if not substring:
        ok = any( filter(lambda u:u in UCDs, set(l)) )
    else:
        ok = []
        for u in l:
            ok.append(any( [ string.find(u,ucd)>=0 for ucd in UCDs ] ))
        ok = any(ok)
    return ok

def getUnit(tab):
    """Returns a list of units from a table"""
    l = []
    for f in tab.fields():
        if not f.unit:
            continue
        _u = str(f.unit).replace(' ','')
        if not _u in l:
            l.append(_u)
    return l

def checkUnits(tab,Units=[]):
    """Returns a True if tb has one of the given Units; False otherwise"""
    if tab is None:
        return None
    if not Units:
        return True
    l = getUnit(tab)
    ok = any( filter(lambda u:u in Units, set(l)) )
    return ok

# Astropy
"""
from astropy.io.votable.ucd import UCDWords,parse_ucd
from astropy.io.votable.tree import Table
from astropy.utils import data

class Tree(object):
    def __init__(self,UCDs):
        '''
        Build the tree of UCDs given in list
        '''
        self._original = list
        self._store = {}

        dictList = []
        for ucd in self._original:
            ucd = self.split(ucd)
            if ucd:
                dictList.append(ucd)
        aux = {}
        for d in dictList:
            self.merge(d,aux)

    def split(self,ucd):
        if ucd is None:
            return None
        words = ucd.split('.')  # 'words' can be a (list of) one-word UCD
        d = [str(words.pop())]
        words.reverse()
        for w in words:
            d = {w:d}
        return d          # Notice that a single string can be returned

    def merge(self,node,ref):
        if isinstance(node,dict):
            k,v = node.popitem()
            assert(len(node)==0)
            if isinstance(ref,dict):
                if k in ref.keys():
                    self.merge(v,ref[k])
                else:
                    ref[k] = v if isinstance(v,dict) else [v]
            else:
                assert(isinstance(ref,list))
                if
        else:
            assert(isinstance(node,list))
            if isinstance(ref,dict):
                if not node in ref.keys():
                    ref[node[0]] = []
            else:
                assert(isinstance(ref,list))
                ref.append(node[0])

        for node in aux:
            if isinstance(node,str):
                strings.append(node)
                continue
            assert(isinstance(node,dict))
            val = node.values()
            assert(len(val)==1)
            val = val.pop()
            if isinstance(val,str):



class UCDTree(object):
    '''
    Builds a hierarchical view of acceptable UCD words

    The code here is based on the `~astropy.io.votable.ucd.UCDWords` code.
    Works by reading in a data file exactly as provided by IVOA.
    This file resides in data/ucd1p-words.txt.
    '''
    def __init__(self):
        self._tree = {}
        self._descriptions = {}
        self._capitalization = {}

        with data.get_pkg_data_fileobj(
                "data/ucd1p-words.txt", encoding='ascii') as fd:
            tree = {}
            for line in fd.readlines():
                type, name, descr = [
                    x.strip() for x in line.split('|') ]
                name_lower = name.lower()

def fromField(field):
    assert(hasattr(field,'ucd'))
    return field.ucd

def _parsePlain(votable):
    assert(isinstance(votable,Table))
    out = []
    for f in votable.fields:
        ucd = fromField(f)
        if ucd is None:
            continue
        l = [ str(u[1]) for u in parse_ucd(ucd) ]
        out.extend(l)
    return out

def _parseTree(votable):
    assert(isinstance(votable,Table))
    out = {}
    for f in votable.fields:
        ucd = fromField(f)
        if ucd is None:


def fromTable(votable,mode='plain'):
    '''
    Return a plain list with all table's UCDs

    Input:
     - mode : way to output UCDs. Options are ['plain','tree']
    '''
    assert(isinstance(votable,Table))
    assert(mode== 'plain' or mode=='tree')
    if mode=='plain':
        return _parsePlain(votable)
    else:
        return _parseTree(votable)

"""
