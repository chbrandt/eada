import pyvo

from . import constants

from . import registry
from . import scs

from pyvo.dal.query import DALQueryError,DALServiceError

class ServiceError(DALServiceError):
    def __init__(self):
        super(ServiceError,self).__init__()

class QueryError(DALQueryError):
    def __init__(self):
        super(QueryError,self).__init__()
