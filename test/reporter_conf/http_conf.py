from sseclient import SSEClient
import datetime, functools

# URL = 'http://192.168.0.89:5005'
# URL = 'http://121.67.47.157:8881'
# URL = 'http://indycare.neuromeka.com:8881'
URL = 'http://127.0.0.1:5005'


def check_timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = datetime.datetime.now()
        res = func(*args, **kwargs)
        #if res.text:
        #    print(json.loads(res.text))
        t1 = datetime.datetime.now()
        print(t0, t1 - t0)
        return res
    return wrapper


@check_timing
def POST(s, url, **kwargs):
    return s.post(URL + url, **kwargs)


@check_timing
def GET(s, url, **args):
    return s.get(URL + url, **args)


@check_timing
def PUT(s, url, **kwargs):
    return s.put(URL + url, **kwargs)


@check_timing
def DELETE(s, url, **kwargs):
    return s.delete(URL + url, **kwargs)
