# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 13:57:09 2014

@author: chbrandt
"""

class Format:
    
    class Color:
        green   = '\033[92m'
        red     = '\033[91m'
        white   = '\033[0m'
        
        ok      = green
        fail    = red
        normal  = white
