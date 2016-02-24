#-*- coding:utf-8 -*-

from eada import *

from astropy.table.table import Table
from pyvo.dal.ssa import SSARecord
TIMEOUT=10

# --
class Aux:

    @staticmethod
    def enrich_columns(table,ssa_record,ssa_columns):
        """
        Verify whether given column names do exist in 'table'

         Columns (which is supposed to be a list of column names) should match with
        table's contents. The columns that do not match with table's will simply
        be discarded from the output list.

        Note: empty column name is not allowed and will be discarded.

        Input:
         - table   : py:class:`~astropy.table.table.Table`
         - columns : [str]
             Column names to verify/match against table ones

        Output:
         - [str]
             List of column names matching table' columns.
        """
        def create_column_from_value(value,length,name):
            from astropy.table import Column
            col = Column([value]*length,name=name)
            return col

        assert isinstance(table,Table)
        assert isinstance(ssa_columns,list)
        assert isinstance(ssa_record,SSARecord)
        columns = ssa_columns
        record = ssa_record

        rcols = record.keys()
        logging.debug("Table columns: %s" % ','.join(rcols))

        leng = len(table)

        cols = []
        for i,col in enumerate(columns):
            assert isinstance(col,str)
            c = col.strip()
            del col
            if not c:
                logging.warning("Empty column name at position %d" % i)
                continue
            if not c in rcols:
                logging.warning("Column name '%s' not found in table" % c)
                continue
            val = record.get(c,None)
            cols.append( create_column_from_value(val,leng,name=c))

        logging.debug("Selected columns: %s" % cols)

        return cols

    @staticmethod
    def open_spec(file,format):
        """
        Read table from FITS/VOTable file
        """
        from astropy.table import Table
        tab = None
        if format is 'fits':
            # I am assuming the table of interest it at the first BinTableHDU
            hdu_index = 1
            tab = Table.read(file,format=format,hdu=hdu_index)
        elif format is 'votable':
            tab = Table.read(file,format=format)
        else:
            print("Format {} not supported (using Astropy's Table).".format(format))
        return tab

    @staticmethod
    def options(key):
        _options = {
            'format' : """
                all       all formats available
                compliant any SSA data model compliant format
                native    the native project specific format for the spectrum
                graphic   any of the graphics formats: JPEG, PNG, GIF
                votable   the SSA VOTable format
                fits      the SSA-compliant FITS format
                xml       the SSA native XML serialization
                metadata  no images requested; only an empty table with fields
                          properly specified
                """,
        }
        if not _options.has_key(key):
            print("Don't know such option. Can be a typo or I'm missing it. Check the docs.")
        print _options[key]

    @staticmethod
    def resolve_name(name):
        """
        Resolve object name, return its ICRS position in degrees
        """
        from astropy.coordinates import get_icrs_coordinates as get_coords
        try:
            icrs = get_coords(name)
            pos = (icrs.ra.value,icrs.dec.value)
        except:
            pos = None
        return pos

    @staticmethod
    def download_spec(record,dir='ssafiles'):
        from os import mkdir
        from os import path
        f = record.format
        if not path.isdir(dir):
            mkdir(dir)
        record.cachedataset(dir=dir)
        return path.join(dir,record.make_dataset_filename())


# --
def specsearch(ra,dec,radius,url,format=None,timeout=None):
    """
    Search for objects inside the circle (ra,dec,radius) at given 'url'

    It is supposed to find a ssap service at the given 'url' address.

    Input:
     - ra      : float
                 right ascension [degrees]
     - dec     : float
                 declination [degrees]
     - radius  : float
                 search radius [degrees]
     - url     : string
                 url of the service to query/retrieve
     - format  : string
                 format of spectra file(s) to be returned
     - timeout : int
                 time (seconds) to wait for a response

    Output:
     - SSAResults (py:class:`~pyvo.dal.ssa.SSAResults`)
         Conesearch service result. 'None' is returned in case of error.

    """
    db_url = url

    logging.debug("Position (%s,%s) and radius (%s), in degrees" %(ra, dec, radius))
    logging.debug("URL (%s) and timeout (%s)" % (url, timeout))

    from pyvo.dal import ssa
    from pyvo.dal import query

    if timeout and isinstance(timeout,(int,float)):
        timeout = ((timeout*1.0)+0)/1.0 # sanity check
        try:
            query.setparam('timeout',timeout)
        except:
            logging.warning("'timeout' parameter not set on query.")

    res = None
    q = ssa.SSAQuery(url)
    q.pos = (ra,dec)
    q.size = radius
    if format:
        q.format = format
    q.verbosity = 3
    try:
        res = q.execute()
    except query.DALServiceError as e:
        logging.exception("DALServiceError raised: %s"%(e))
    except query.DALQueryError as e:
        logging.exception("DALQueryError raised: %s"%(e))
    except Exception as e:
        logging.exception("Exception raised: %s"%(e))

    return res

def concatenate_tables(tables):
    """
    Concatenate (columns) of given tables
    """
    from astropy.table import vstack
    tab = vstack(tables, join_type='outer')
    return tab

# --
def main(ra,dec,radius,url,columns=[]):
    """
    Query SSA service and return a 'columns'-filtered table

    Input:
     - ra      : float
                 right ascension [degrees]
     - dec     : float
                 declination [degrees]
     - radius  : float
                 search radius [degrees]
     - url     : string
                 url of the service to query/retrieve
     - columns : list-of-strings
                 name of the collumns to keep in the output table

    Output:
     - Table (py:class:`~astropy.table.table.Table`)
         Retrieved table, 'columns'-filtered. 'None' is returned in case of error

    """
    logging.info(Doc.synopsis(main))
    logging.info("Position (%s,%s) and radius (%s), in degrees" %(ra, dec, radius))
    logging.info("URL (%s) and columns (%s)"%(url, columns))

    #TODO: support object name resolution
    ssaTab = specsearch(ra,dec,radius,url)
    if ssaTab is None:
        logging.error("Search failed to complete. Service not working properly. Exiting")
        return None

    #TODO: How to deal with multiple results?!!!
    tables = []
    for rec in ssaTab:
        filecache = Aux.download_spec(rec)
        if 'fits' in rec.format:
            format = 'fits'
        elif 'votable' in rec.format:
            format = 'votable'
        else:
            format = None
        tab = Aux.open_spec(filecache,format)
        if tab is None:
            continue
        # Garantee we don't have empty column names and names that match tble ones..
        if columns:
            cols = Aux.enrich_columns(tab,rec,columns)
            tab.add_columns(cols)

        tables.append(tab)

    if len(tables) == 0:
        logging.error("No tables were found. Exiting")
        return None

    tab = concatenate_tables(tables)

    logging.info("Retrieved table has %d objects, %d columns." % (len(tab),len(tab.colnames)))
    return tab
