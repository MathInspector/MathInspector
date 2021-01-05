import inspect, re, string
from .docscrape import FunctionDoc

RE_FN = re.compile(r"[a-zA-Z_0-9]*\((.*)\)")
RE_EXTRA = re.compile(r"(\[.*\])")

def argspec(obj, withself=True):
    if isinstance(obj, dict):
        return [], {}

    try:
        fullargspec = inspect.getfullargspec(obj)
    except:
        fullargspec = None

    if fullargspec and callable(obj):
        num_kwargs = len(fullargspec[3]) if fullargspec[3] else 0
        args = fullargspec[0][0 if withself else 1:len(fullargspec[0]) - num_kwargs]
        num_args = len(args) if withself else 1 + len(args)
        kwargs = {}
        if num_kwargs > 0:
            kwargs = { fullargspec[0][i]:fullargspec[3][i - num_args] for i in range(num_args, len(fullargspec[0])) }
        if fullargspec[5] and len(fullargspec[5]) > 0:
            for name in fullargspec[5]:
                kwargs[name] = fullargspec[5][name]
    
        return args, kwargs

    try:
        doc = FunctionDoc(obj)
    except:
        return ['x'], {}
    
    signature = doc["Signature"].replace(", /", "").replace(", \*", "").replace(", *", "")
    signature = RE_EXTRA.sub("", signature)
    params = RE_FN.findall(signature)
    if len(params) == 0:
        return False
    items = [i.lstrip() for i in params[0].split(",")]  

    args = [i for i in items if "=" not in i]
    kwargs = { i.split("=")[0] : eval(i.split("=")[1]) for i in items if "=" in i}

    return args, kwargs