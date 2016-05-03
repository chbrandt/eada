#-*- coding:utf-8 -*-

import logging

LOGLEVEL=logging.DEBUG

class Arguments(object):

    def __init__(self,description):
        import argparse
        self.stop = False
        self.foo = None
        self.parser = argparse.ArgumentParser(description=description)
        self.init_arguments()

    def _break(self,foo):
        self.stop = True
        self.foo = foo

    def init_arguments(self):
        self.parser.add_argument('--logfile', nargs='?', default=None,
                                const='vos.log',
                                help="Write a logfile. Default is 'vos.log'.")

    def parse_arguments(self,args):
        args = self.parser.parse_args(args)
        #self.parser.parse_args(args, namespace=self)
        self.args = vars(args)
        self.setup_log()

    def setup_log(self):
        lf = self.get('logfile')
        if lf:
            logging.basicConfig(filename=lf, filemode='w',
                                format='[%(filename)s:%(funcName)20s] %(message)s',
                                level=LOGLEVEL)
        else:
            logging.disable(logging.NOTSET)

        self.set('logfile',lf)

    def arguments(self):
        return self.args.copy()

    def get(self,arg):
        return self.args.get(arg)

    def set(self,arg,val):
        self.args[arg] = val


class ServArguments(Arguments):

    def __init__(self,description):
        super(ServArguments,self).__init__(description)

    def init_arguments(self):
        super(ServArguments,self).init_arguments()
        # Mutually exclusive options
        #  The options are meant to be "list" or "choose" catalogues or give the
        #  "url" directly.
        #
        servers = self.parser.add_mutually_exclusive_group(required=True)

        servers.add_argument('--list', action='store_true',
                            help="Print the list os servers available for the search.")

#        SRVS = availableCatalogs(cp) if cp else []
        SRVS = []
        servers.add_argument('--server', #dest='cat', metavar='CATALOG',
                            choices = SRVS,
                            help="Server/service to search. To see your choices use the '--list' option.")

        servers.add_argument('--url',
                            help="Service URL to query. To see some options use the '--list' option.")


    def parse_arguments(self,args):
        super(ServArguments,self).parse_arguments(args)

        lst = self.get('list')
        srv = self.get('server')
        url = self.get('url')
        # in practice this assert will never be used,
        assert srv or url or lst # (it is done by the argparse)
        # i'll leave it here anyway as a sanity check...
        if lst:
            self.list()
        else:
            if not url and srv not in cp.keys():
                logging.critical("Wrong catalog name: %s", srv)
                print "Given catalog ('%s') is not known. Try a valid one (-h)." % (srv)
                print "Finishing here."
                sys.exit(1)

            if url:
                logging.debug("URL to search for sources: %s", url)
            else:
                url = cp.get(srv)['url']
                logging.debug("Service (%s) url: %s", srv, url)

            self.set('url',url)

    def list(self):
        def foo():
            print "list of bla"
            return 0
        self._break(foo)

class LocArguments(ServArguments):

    def __init__(self,description):
        super(LocArguments,self).__init__(description)

    def init_arguments(self):
        super(LocArguments,self).init_arguments()
        # (redundant) Group of options for better organize arguments
        #
        loc = self.parser.add_argument_group('Location','Defining a object/position to search for.')

        loc.add_argument('--ra', dest='ra', type=float, default=0,
                                help="Right Ascension of the object (in degrees by default)")

        loc.add_argument('--dec', dest='dec', type=float, default=0,
                                help="Declination of the object (in degrees by default)")

        loc.add_argument('--radius', type=float, dest='radius', default=0.00001,
                                help="Radius (around RA,DEC) to search for object(s)",)

        loc.add_argument('--runit', dest='runit', metavar='unit', default='degree',
                                choices=['degree','arcmin','arcsec'],
                                help="Unit for radius value. Choices are 'degree','arcmin','arcsec'.")

    def parse_arguments(self,args):
        super(LocArguments,self).parse_arguments(args)

        from astropy import units
        ra = self.get('ra')
        dec = self.get('dec')
        logging.debug('RA:%s , DEC:%s', ra, dec)

        radius = self.get('radius')
        ru = ''
        if self.get('runit') == 'degree':
            ru = units.degree
        elif self.get('runit') == 'arcmin':
            ru = units.arcmin
        elif self.get('runit') == 'arcsec':
            ru = units.arcsec
        else:
            logging.error("Radius' unit is not valid. Use 'degree', 'arcmin' or 'arcsec'.")
            sys.exit(EXIT_ERROR)

        rad = radius*ru
        logging.debug('Radius %s', rad)
        radius = rad.to(units.degree).value # convert the given radius to degrees
        del rad

        self.set('ra',ra)
        self.set('dec',dec)
        self.set('radius',radius)
