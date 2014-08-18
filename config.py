#!/usr/bin/env python
import ConfigParser

FILE = "conesearch.cfg"

def parse(catalog=None):
  cp = ConfigParser.ConfigParser()
  cp.read(FILE)
  if not (catalog is None):
    if not cp.has_section(catalog):
      return None

  ret = {}
  if catalog is None:
    for catalog in cp.sections():
      cat = {}
      for opt,val in cp.items(catalog):
        cat[opt] = val
      assert(cat['url'])
      ret[catalog] = cat
  else:
    cat = {}
    for opt,val in cp.items(catalog):
      cat[opt] = val
    assert(cat['url'])
    ret[catalog] = cat
  return ret

