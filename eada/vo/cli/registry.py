#!/usr/bin/env python

_DESCRIPTION = """Search (USVAO) registry for services."""

from ..constants import WAVEBANDS,SERVICES
from . import Arguments


class RegArguments(Arguments):
    def __init__(self,description):
        super(RegArguments,self).__init__(description)

    def init_arguments(self):
        super(RegArguments,self).init_arguments()
        self.parser.add_argument('service',
                                choices=SERVICES.keys(),
                                help='Service (resource) to search for.')

        self.parser.add_argument('--wavebands',
                                choices=WAVEBANDS.keys(),
                                const=None, default=None,
                                action='store',
                                help='Waveband of interest to search for.')

        self.parser.add_argument('--keywords',
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

    def parse_arguments(self,args):
        super(RegArguments,self).parse_arguments(args)
