class Aux:

    @staticmethod
    def concatenate_tables(tables):
        """
        Concatenate (columns) of given tables
        """
        from astropy.table import vstack
        tab = vstack(tables, join_type='outer')
        return tab

    @staticmethod
    def filter_columns(table,columns):
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
        assert(isinstance(table,Table))
        assert(isinstance(columns,list))

        tcols = table.colnames
        logging.debug("Table columns: %s" % tcols)

        cols = []
        for i,col in enumerate(columns):
            assert(isinstance(col,str))
            c = col.strip()
            if not c:
                logging.warning("Empty column name at position %d" % i)
                continue
            del c
            if not col in tcols:
                logging.warning("Column name '%s' not found in table" % col)
                continue
            cols.append(col)

        logging.debug("Selected columns: %s" % cols)
        return cols

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
        return table.add_columns(cols)

    @staticmethod
    def open_spec(file,format):
        """
        Read table from FITS/VOTable file
        """
        from astropy.table import Table
        tab = None
        if 'fits' in format:
            # I am assuming the table of interest it at the first BinTableHDU
            hdu_index = 1
            tab = Table.read(file,format='fits',hdu=hdu_index)
        elif 'votable' in format:
            tab = Table.read(file,format='votable')
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
