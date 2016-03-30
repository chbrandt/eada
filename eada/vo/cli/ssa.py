#-*- coding:utf-8 -*-

_DESCRIPTION = """Search SSA services for objects."""

#from ..constants import WAVEBANDS,SERVICES
from common import LocArguments


class SSA(object):
    def __init__(self,description=None):
        if not description:
            description = _DESCRIPTION
        self.init_arguments(description)

    def init_arguments(self,desc):
        #from registry import RegArguments
        self.arguments = SSAArguments(desc)

    def search(self,args):
        from eada import vo as vos
        self.arguments.parse_arguments(args)
        args = self.arguments.dargs()
        table = vos.ssa.search(**args)


class SSAArguments(LocArguments):
    def __init__(self,description):
        super(SSAArguments,self).__init__(description)

    def init_arguments(self):
        super(SSAArguments,self).init_arguments()
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
        super(SSAArguments,self).parse_arguments(args)

        if self.args.cols:
            if 'asdc' in self.args.cols:
                if self.args.url:
                    cols = []
                else:
                    dcat = cp.get(cat)
                    if dcat.has_key('columns'):
                        cols = dcat.get('columns')
                        cols = string.split(cols,',')
                    else:
                        cols = []
            else:
                cols = self.args.cols
        else:
            cols = []
        logging.debug("Columns to output: %s", cols)

        self.cols = cols

    def list(self):
        print "list of spectra"
