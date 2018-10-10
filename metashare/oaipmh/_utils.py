# coding=utf-8
import json
import time

def get_values(dictionary, parameters):
    """
    Check parameters and return the values or raise
    AttributeError if missing.
    """
    try:
        values = [dictionary[par] for par in parameters]
    except Exception, exc:
        raise exc
    else:
        return values[0] if len(values)==1 else values

def prehtmlify(obj, add_pre=True):
    """
    Make object nicely displayable in <pre>.
    """
    if obj:
        str_ = u"%s" % json.dumps(obj, indent=2)
        return u"<pre style=\"margin:0;font-size:8pt\">%s</pre>" % str_ \
            if add_pre else str_
    return u"Invalid"


def smart_extend(dict_inst, *dict_arr):
    """
    Recursively add items at every level to
    dict_inst rather than simply update.
    """
    for item in dict_arr:
        dict_inst.update(item)
    return dict_inst

def time_it(func, *args, **kwargs):
    """
    Time a function.
    Alternative implement as a decorator.
    """
    start = time.time()
    ret = func(*args, **kwargs)
    end = time.time()
    return end - start, ret

def html_mark_error(text):
    """ Simple mark error using html and css. """
    return u"<div style='color:red;'>%s</div>" % text

def html_mark_warning(text):
    """ Simple mark warning using html and css. """
    return u"<div style='color:orange;'>%s</div>" % text