#-*- coding:utf-8 -*-

_DESCRIPTION = """Search (USVAO) registry for services."""

import logging

def run(argv,desc=None):
    """
    Run regsearch cli: resolve arguments, return Table
    """
    from _run import search,write
    from eada import vo as vos

    if not desc:
        desc = _DESCRIPTION
    argParser = RegArguments(desc)

    table = search(argv,argParser,vos.registry.search)

    res = write(argv,argParser,vos.registry.write,table)

    return res


from .arguments import Arguments
from ..constants import WAVEBANDS,SERVICES

class RegArguments(Arguments):
    def __init__(self,description):
        super(RegArguments,self).__init__(description)

    def init_arguments(self):
        super(RegArguments,self).init_arguments()
        self.parser.add_argument('service',
                                choices=SERVICES.keys(),
                                help='Service (resource) to search for.')

        self.parser.add_argument('--waveband',
                                choices=WAVEBANDS.keys(),
                                const=None, default=None,
                                action='store',
                                help='Waveband of interest to search for.')

        self.parser.add_argument('--keywords', nargs='*',
                                const=None, default=None,
                                action='store',
                                help='Keywords to be found (anywhere) in resources.')

        self.parser.add_argument('--ucds',
                                const=None, default=None,
                                action='store',
                                help='UCDs to be found in resources.')

        self.parser.add_argument('--units',
                                const=None, default=None,
                                action='store',
                                help='Units to be found in resources.')

        self.parser.add_argument('--output', default='resources.ini',
                                 help="File (.ini) to output selected resources.")


    def parse_arguments(self,args):
        super(RegArguments,self).parse_arguments(args)
