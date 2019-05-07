import os
import json

_BASEDIR = '.eada'
_BASEDIR = os.path.join(os.path.abspath(os.environ['HOME']), _BASEDIR)

_BASEDIR_REG = os.path.join(_BASEDIR, 'epntap')

if not os.path.exists(_BASEDIR_REG):
    os.makedirs(_BASEDIR_REG)


def write_to_cache(content_json):
    cache = os.path.join(_BASEDIR_REG, 'registry.json')
    content_json.to_json(cache, orient='records')
    # try:
    #     fp = open(cache, 'w')
    # except PermissionError:
    #     return "Cache file cannot be written."
    # else:
    #     with fp:
    #         json.dump(content_json, fp)


def read_from_cache():
    cache = os.path.join(_BASEDIR_REG, 'registry.json')
    try:
        fp = open(cache, 'r')
    except PermissionError:
        return "Cache file cannot be read."
    else:
        with fp:
            return json.load(fp)

def path_registry_cache():
    return os.path.join(_BASEDIR_REG, 'registry.json')
