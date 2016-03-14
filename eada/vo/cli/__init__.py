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
        args,unkn = self.parser.parse_args(args)
        self.args = args
        self.setup_log()

    def setup_log(self):
        if self.args.log:
            logging.basicConfig(filename=args.log, filemode='w',
                                format='[%(filename)s:%(funcName)20s] %(message)s',
                                level=LOGLEVEL)
        else:
            logging.disable(logging.NOTSET)


class Registry(object):
    def __init__(self,description=None):
        if not description:
            description = _DESCRIPTION
        self.init_arguments(description)

    def init_arguments(self,desc):
        from registry import RegArguments
        self.arguments = RegArguments(desc)

    def parse_arguments(self,args):
        self.arguments.parse_arguments(args)

    def main(self,args):
        self.parse_arguments(args)
