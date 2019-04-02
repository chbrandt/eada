# -*- coding:utf-8 -*-
"""
Base module for the library, where common modules/functions are loaded/defined.
"""
from __future__ import print_function, absolute_import

from astropy import log as logging
# import logging

## Namespace to dealt with docstrings
#
class Doc:
    """
    Auxiliary functions to deal with python docstrings
    """
    @staticmethod
    def synopsis(foo):
        """
        Return a functions short description
        """
        import pydoc
        doc = foo.func_doc
        s = pydoc.splitdoc(doc)[0]
        return s
    short = synopsis


## Typed lists
#
class TypedList(list):
    """
    Specialization of 'list' to store homogeneous/typed objects
    """

    def __init__(self,type):
        """
        Constructor
        """
        self._type = type

    def append(self,item):
        """
        Append an item

        Raise TypeError in case of non-matching item/list types
        """
        if not isinstance(item,self._type):
            raise TypeError, "item is not of type %s" % self._type
        super(TypedList,self).append(item)

class StringList(TypedList):
    """
    Specialization of py:class:`~TypedList` to deal with strings
    """

    def __init__(self,allowEmptyItems=False):
        """
        Constructor

        Parameters:
         - allowEmptyItems : (en/dis)able to store empty/white-space strings
        """
        super(StringList,self).__init__(str)
        self._allowEmptyItems = allowEmptyItems

    def append(self,item,strip=False):
        """
        Append a string

        Parameters:
         - strip : bool
             Whether to remove or not leading/trailing white-spaces
        """
        s = item.strip()
        if (not self._allowEmptyItems) and (not s):
            return
        if strip:
            item = s
        super(StringList,self).append(item)
