#-*- coding:utf-8 -*-

_DESCRIPTION = """Search SCS services for objects."""

import logging

def run(args,desc=None):
    """
    """
    from .run import search
    from eada import vo as vos

    if not desc:
        desc = _DESCRIPTION
    arguments = SCSArguments(desc)

    table = search(arguments,vos.scs.search)

    return table


from .arguments import LocArguments

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
        def foo():
            print "list of catalogs"
            return 0
        self._break(foo)

# class SCS(object):
#     def __init__(self,description=None):
#         if not description:
#             description = _DESCRIPTION
#         self.init_arguments(description)
#
#     def init_arguments(self,desc):
#         #from registry import RegArguments
#         self.arguments = SCSArguments(desc)
#
#     def search(self,args):
#         from eada import vo as vos
#         self.arguments.parse_arguments(args)
#         args = self.arguments.arguments()
#         # ---
#         from inspect import getargspec
#         foo_args = getargspec(vos.scs.search)[0]
#         args = _filter_dict(args,foo_args)
#         # ---
#         table = vos.scs.search(**args)
#         return table
