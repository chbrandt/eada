
class Waveband(dict):
    """Base class to define a waveband"""
    def __init__(self):
        super(Waveband,self).__init__()
        self.ucd = None

class Radio(Waveband):
    def __init__(self):
        super(Radio,self).__init__()
        self.ucd = 'em.radio'

class Millimeter(Waveband):
    def __init__(self):
        super(Millimeter,self).__init__()
        self.ucd = 'em.mm'

class Infrared(Waveband):
    def __init__(self):
        super(Infrared,self).__init__()
        self.ucd = 'em.IR'

class Optical(Waveband):
    def __init__(self):
        super(Optical,self).__init__()
        self.ucd = 'em.opt'

class Ultraviolet(Waveband):
    def __init__(self):
        super(Ultraviolet,self).__init__()
        self.ucd = 'em.UV'

class Xray(Waveband):
    def __init__(self):
        super(Xray,self).__init__()
        self.ucd = 'em.X-ray'

class Gammaray(Waveband):
    def __init__(self):
        super(Gammaray,self).__init__()
        self.ucd = 'em.gamma'

# Wavebands available to search for catalogue data
# (for convenience I relate the UCD words used)
# For UCDs, take a look at http://www.ivoa.net/documents/latest/UCDlist.html
#
WAVEBANDS = {'radio'        : Radio(),
             'millimeter'   : Millimeter(),
             'infrared'     : Infrared(),
             'optical'      : Optical(),
             'uv'           : Ultraviolet(),
             'xray'         : Xray(),
             'gammaray'     : Gammaray()}

SERVICES = {'scs' : None,
            'ssa' : None}
