from urllib.parse import urlparse, parse_qs, urlencode

import ast


def encode_state(component_ids_zipped, values):
    """
    return a urlencoded string that encodes the current state of the app
    (as identified by component_ids+values)

    First encodes as a list of tuples of tuples of :
    (component_id, (parameter, value))

    This then gets encoded by urlencode as two separate querystring parameters
    e.g. ('tabs', ('value', 'cs_tab')) will get encoded as:
          ?tabs=value&tabs=cs_tab
    """

    statelist = [(component_ids_zipped[0][i],
                    (component_ids_zipped[1][i],
                    values[i]))
                    for i in range(len(values))
                    if  values[i] is not None]

    params = urlencode(statelist,  doseq=True)
    return f'?{params}'


def parse_state(url):
    """
    Returns a dict that summarizes the state of the app at the time that the
    querystring url was generated.

    The querystring parameters come in pairs (see above), e.g.:
              ?tabs=value&tabs=cs_tab

    This will then be encoded as dictionary with the component_id as key
    (e.g. 'tabs') and a list (param, value) pairs (e.g. ('value', 'cs_tab')
    for that component_id as the item.

    lists (somewhat hackily detected by the first char=='['), get evaluated
    using ast.

    Numbers are appropriately cast as either int or float.
    """

    parse_result = urlparse(url)

    statedict = parse_qs(parse_result.query)
    if statedict:
        for key, value in statedict.items():
            statedict[key] = list(map(list, zip(value[0::2], value[1::2])))
            # go through every parsed value pv and check whether it is a list
            # or a number and cast appropriately:
            for pv in statedict[key]:
                # if it's a list
                if isinstance(pv[1], str) and pv[1][0]=='[':
                    pv[1] = ast.literal_eval(pv[1])

                #if it's a number
                if (isinstance(pv[1], str) and
                    pv[1].lstrip('-').replace('.','',1).isdigit()):

                    if pv[1].isdigit():
                        pv[1] = int(pv[1])
                    else:
                        pv[1] = float(pv[1])
    else: #return empty dict
        statedict = dict()
    return statedict


def apply_value_from_querystring(params):
    """
    Funky function wrapper that looks up the component_id in the
    querystring parameter statedict, and if it finds it, loops
    through the (param, value) combinations in the (item) list
    and assign the right value to the right parameter.

    Every component that is saved in the querystring needs to be wrapped
    in this function in order for the saved parameters to be assigned
    during loading.
    """
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if 'id' in kwargs and kwargs['id'] in params:
                param_values = params[kwargs['id']]
                for pv in param_values:
                    kwargs[pv[0]] = pv[1]
            return func(*args, **kwargs)
        return apply_value
    return wrapper
