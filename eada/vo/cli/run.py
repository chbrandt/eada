#-*- coding:utf-8 -*-

class Aux:
    @staticmethod
    def filter_dict(dictionary,keys):
        _d = { key : dictionary[key] for key in keys }
        return _d

def search(argv,argparser,foo_search):
    """
    """
    from .arguments import Arguments
    assert isinstance(argparser,Arguments)
    from inspect import isfunction
    assert isfunction(foo_search)

    argparser.parse_arguments(argv)
    if argparser.stop:
        ret = argparser.foo()
        return ret
    args = argparser.arguments()

    from inspect import getargspec
    foo_args = getargspec(foo_search)[0]
    args = Aux.filter_dict(args,foo_args)

    table = foo_search(**args)
    return table
