""" Initialization file for a GDC API client.
"""

from copy import copy
import types

from .client import BaseClient

# Aliases
COMMON_ALIASES = {
    "_get_cases": 'get_cases',
    "_get_fields": 'get_fields'
        }

# API specific aliases
GDCAPI_ALIASES = copy(COMMON_ALIASES)

# Kwargs
COMMON_KWARGS = {
    "_default_url": 'https://api.gdc.cancer.gov',
    "_projects_endpoint": '/projects',
    "_files_endpoint": '/files',
    "_cases_endpoint": '/cases',
    "_app_id": None,
    "_app_key": None,
}

# API specific kwargs
GDCAPI_KWARGS = copy(COMMON_KWARGS)

# GDC client settings
CLIENT_SETTINGS = {
    "gdc": {
        "class_name": 'GdcClient',
        "class_kwargs": GDCAPI_KWARGS,
        "attr_aliases": GDCAPI_ALIASES,
        "base_class": BaseClient,
        "mixins": []
    },
}

def copy_func(f, name=None):
    """ Returns a function with the same code, globals, defaults, closure, and name (unless provided a different name).
    """
    fn = types.FunctionType(f.__code__,
                            f.__globals__, name or f.__name__,
                            f.__defaults__,
                            f.__closure__)
    fn.__dict__.update(f.__dict__)
    return fn

def get_client(api=None, instance=True, *args, **kwargs):
    """ Function that returns the necessary Edemam API client.

    :param api: The api wrapper to be returned.
    :type api: str
    """
    if not api:
        url = kwargs.get('url', False)
        if not url:
            raise RuntimeError('No API type or url specified.')
    api = api.lower()
    if (api not in CLIENT_SETTINGS and not kwargs.get('url', False)):
        raise Exception('No api {}, currently avaliable. Available apis are: {}'.format(api, list(CLIENT_SETTINGS.keys())))

    _settings = CLIENT_SETTINGS[api]
    _class = type(_settings["class_name"], tuple([_settings["base_class"]] + _settings["mixins"]), _settings["class_kwargs"])
    # Set aliases
    for (src_attr, target_attr) in _settings["attr_aliases"].items():
        if getattr(_class, src_attr, False):
            setattr(_class, target_attr, copy_func(getattr(_class, src_attr), name=target_attr))
    _client = _class(*args, **kwargs) if instance else _class
    return _client

class GdcClient(get_client('gdc', instance=False)):
    pass
