#-*- coding:utf-8 -*-

class Aux:
    @staticmethod
    def filter_dict(dictionary,keys):
        _d = { key : dictionary[key] for key in keys }
        return _d

def search(arguments,foo_search):
    """
    """
    from .arguments import Arguments
    assert isinstance(arguments,Arguments)

    arguments.parse_arguments(args)
    if arguments.stop:
        ret = arguments.foo()
        return ret
    args = arguments.arguments()

    from inspect import getargspec
    foo_args = getargspec(foo_search)[0]
    args = Aux.filter_dict(args,foo_args)

    table = foo_search(**args)
    return table
