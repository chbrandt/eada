#-*- coding:utf-8 -*-

_DESCRIPTION = """Search SCS services for objects."""

import logging

def run(argv,desc=None):
    """
    Run conesearch cli: resolve arguments, return Table
    """
    from _run import search
    from eada import vo as vos

    if not desc:
        desc = _DESCRIPTION
    argParser = SCSArguments(desc)

    table = search(argv,argParser,vos.scs.search)

    return table


from arguments import LocArguments

class SCSArguments(LocArguments):
    def __init__(self,description):
        super(SCSArguments,self).__init__(description)

    def init_arguments(self):
        super(SCSArguments,self).init_arguments()
        # Output generation options
        #
        output = self.parser.add_argument_group('Output','Options for output generation.')
        output.add_argument('--columns', dest='cols', metavar='fieldname', nargs='*',
                            help="Columns to get from the retrieved catalog. The\
                             argument 'default' will output the preset of columns\
                             set in the config file.")
        output.add_argument('--short', action='store_true',
                            help="Just outputs if at least one source was found.")
        output.add_argument('-o','--outfile', dest='outfile', nargs='?', const='',
                            default=None, help="Filename to write the output, CSV format table file.")

    def parse_arguments(self,args):
        super(SCSArguments,self).parse_arguments(args)

        cols = self.get('columns')
        if cols:
            if 'asdc' in cols:
                if self.args.url:
                    cols = []
                else:
                    dcat = cp.get(cat)
                    if dcat.has_key('columns'):
                        cols = dcat.get('columns')
                        cols = string.split(cols,',')
                    else:
                        cols = []
#            else:
#                cols = self.args.cols
        else:
            cols = []
        logging.debug("Columns to output: %s", cols)

        self.set('columns',cols)

    def list(self):
        super(SCSArguments,self).list()
