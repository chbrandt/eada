#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
logcrt = logging.critical
logerr = logging.error

_registries = { 'US' : ,
                'EU' : 
              }
def main(waveband,keyword='',service='conesearch',registry='US'):
    '''
    Search and filter services to be used for SED analysis
    '''
    
    if not validRegistry(registry):
        logcrt("Registry not valid. Choices are: %s" % _registries.keys())
        return False
    
    # We use PyVO for querying the registry
    