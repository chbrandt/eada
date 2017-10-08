#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Package to read/write config (ini) files

This module carries functions to read config-like files.
INI files and a simple version of XML are treated on the
following functions.
'''

##@ config
#
# Functions to deal with ini-like configuration files.
# INI files have the following structure:
#
# [section]
#  option = value
#
#
# The function 'read_ini' reads the following structure:
#
# [sectA]
#  key1 = value1
# [sectB]
#  key1 = value1
#  key2 = value2
#
# to a python dictionary as follows:
# {
#  'sectA' : {'key1':'value1'},
#  'sectB' : {'key1':'value1' , 'key2':'value2'}
# }
#
#
# And the function 'write_ini' does exactly the oppose direction, from the
#  the dictionary to the ini-like config file.
#

import logging
import sys
import re
import os

def read_default(config_file):
    # config_file is either 'conesearch.cfg' or 'specsearch.cfg'
    config_dir = os.path.join(os.path.expanduser("~"),'.config','eada')
    config_file = os.path.join(config_dir,config_file)
    if not os.path.exists(config_file):
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except:
                logging.error("Could not create directory {}".format(config_dir))
                return False
        try:
            open(config_file,'a').close()
        except:
            return False
    return read_ini(config_file)

#=====================================
# Read config file (INI) to structure:
#
def read_ini( filename, *sections ):
    '''
    Function to read ".ini"-lyke config files into a python structure.
    (About INI files: http://en.wikipedia.org/wiki/INI_file)

    The function returns a dictionary of dictionaries. That is, the sections "[]"
    of the ini file are dictionaries containing config's key:value parameters.
    And everything (i.e, all sections) is returned inside a dictionary.

    config_struct = read_config( configfile.ini [,'sectionA','sectionB',...])

    If "section..." keys are not given as arguments for the function, it will
    read every section from the file. Otherwise, if a section name (e.g, "sectionA")
    is given, just that section(s) will be returned.

    Input:
     - filename : ini-like configuration file
     - sections : (optional) comma-separated section names
                   If provided, only these sections will be read
    Output:
     - out : dictionary of pairs key-value where key is a section name
                         and value is a dictionary with the items on that 'section'

    '''

    import os
    assert(os.path.isfile(filename))

    import ConfigParser;
    config = ConfigParser.ConfigParser();
    config.read(filename);

    # Just verify the existence of section (on a real cfg file..):
    #
    sects = config.sections();
    if sects == []:
        # print >> sys.stderr, "Config file {} is empty".format(filename);
        return None;

    # Start list of tuples: [('section',section_dictionary), (,) ,...]
    #
    out = {};
    if sections:
        sects = sections

    # Read out specific sections of config file:
    #
    for _section in sects:
        if not config.has_section(_section):
            assert(sections)
            print >> sys.stderr, "Config file does not have section %s" % (_section);
            continue;

        dsect = {};
        for k,v in config.items(_section):
            # support list syntax "[...]" being read
            pat = re.compile("^\[(.*)\]$")
            r = pat.match(v)
            if r != None:
                s = r.group(1).split(',')
                v = [ str(subs).replace(' ','').replace("\'",'') for subs in s ]
            dsect[k] = v;
        out[_section] = dsect;

    return out;

# ---
read_config = read_ini;
# ---

#====================================================
# Write config structure to .ini file:
#
def write_ini( sections, filename ):
    '''
    Function to write a ini-like (config) file given a dictionary.
    (About INI files: http://en.wikipedia.org/wiki/INI_file)

    Input:
     - sections : dictionary-like structure with dictionaries
                         representing sections in config.
     - filename : string with the name of output file

    '''

    if not isinstance(sections,dict):
        print >> sys.stderr, "A dictionary is expected at 'sections' argument."
        return False
    if len(sections) == 0:
        print >> sys.stderr, "Given 'sections' is empty."
        return None

    import ConfigParser;
    config = ConfigParser.RawConfigParser();

    while sections:
        _item = sections.popitem();
        _section = _item[0];
        config.add_section(_section);
        for k,v in _item[1].items():
            config.set(_section, k, v);

    with open(filename,'w') as fp:
        config.write(fp);

    return True;

# ---
write_config = write_ini;
# ---

#=====================================
# Read config file (XML) to structure:
#
def read_xml( config_file, _section='section', _key='scalar', _value='default' ):
    '''
    Reads a config.xml file into a dictionary with "section"->"key":"value".
    '''
    import xml.dom.minidom as xom;

    doc = xom.parse(config_file);

    map = {};
    for node in doc.getElementsByTagName( _section ):
        d_sec = {};
        secao = str(node.getAttribute("id"));
        for node2 in node.getElementsByTagName( _key ):
            id = str(node2.getAttribute("id"));
            dflt = str(node2.getAttribute( _value ));
            d_sec['%s'%(id)] = dflt;
#            print " : ", secao, id, dflt;

        map['%s'%(secao)] = d_sec;

    return map;

# ---
"""
###########################
if __name__ == "__main__" :
    import optparse;

    parser = optparse.OptionParser();
    parser.add_option('-t',
                      dest='configtype', default='ini',
                      help='Type of config file. Options are "ini" or "xml"',
                      metavar='FILE');
    parser.add_option('-f',
                      dest='configfile', default=None,
                      help='Config file to be read',
                      metavar='FILE');
    (options,args) = parser.parse_args();

    configtype = options.configtype
    configfile = options.configfile;

    if configfile == None:
        parser.print_help();
        sys.exit(1);

    if not (configtype == 'ini'  or  configtype == 'xml'):
        print >> sys.stderr, "Wrong config type (%s) given." % (configtype);
        parser.print_help();
        sys.exit(1);

    #    config = read_config(configfile,'input','path','run_flags');
    if ( configtype == 'ini' ):
        config = read_ini(configfile);
    else:
        config = read_xml(configfile);

    print "-";
    while config:
        dic_sect = config.popitem();
        print "%s : \n"%(dic_sect[0]),dic_sect[1];
    print "-";

    sys.exit(0);
"""
