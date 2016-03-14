import pyvo

from pyvo.dal.query import DALQueryError,DALServiceError

import constants

import servsearch as registry

class ServiceError(DALServiceError):
    def __init__(self):
        super(ServiceError,self).__init__()

class QueryError(DALQueryError):
    def __init__(self):
        super(QueryError,self).__init__()
