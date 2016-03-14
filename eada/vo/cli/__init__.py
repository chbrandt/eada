#!/usr/bin/env python

import logging


class Arguments(object):
    def __init__(self,description):
        import argparse
        self.parser = argparse.ArgumentParser(description=description)
        self.init_arguments()

    def init_arguments(self):
        self.parser.add_argument('--logfile', nargs='?', default=None,
                                const='vos.log',
                                help="Write a logfile. Default is 'vos.log'.")

    def parse_arguments(self,args):
        #args,unkn = self.parser.parse_args(args)
        args = self.parser.parse_args(args)
        self.args = args
        self.setup_log()

    def dargs(self):
        return vars(self.args)

    def setup_log(self):
        if self.args.logfile:
            logging.basicConfig(filename=args.logfile, filemode='w',
                                format='[%(filename)s:%(funcName)20s] %(message)s',
                                level=LOGLEVEL)
        else:
            logging.disable(logging.NOTSET)

    def get(self,arg):
        return self.args.get(arg)


class Registry(object):
    def __init__(self,description=None):
        if not description:
            description = _DESCRIPTION
        self.init_arguments(description)

    def init_arguments(self,desc):
        from registry import RegArguments
        self.arguments = RegArguments(desc)

    def search(self,args):
        from eada import vo as vos
        self.arguments.parse_arguments(args)
        args = self.arguments.dargs()
        wbs = args.get('wavebands')
        kws = args.get('keywords')
        ucds = args.get('ucds')
        unts = args.get('units')
        catalogues = vos.registry.search(wbs, kws, ucds, unts)
