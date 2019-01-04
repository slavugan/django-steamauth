from django.http import HttpResponse
from django.conf import settings
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import re, requests

ABSOLUTE_URL = getattr(settings, 'ABSOLUTE_URL', '127.0.0.1:8000')
STEAM_LOGIN_URL = 'https://steamcommunity.com/openid/login'


def get_steam_login_url(response_url, host=None, scheme='https'):
    if 'http' not in response_url:
        host = host or ABSOLUTE_URL
        if use_ssl is not None:
            scheme = 'https' if use_ssl else 'http'
        response_url = "{0}://{1}{2}".format(scheme, host, response_url)

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": response_url,
        "openid.realm": response_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
    }

    return "{0}?{1}".format(STEAM_LOGIN_URL, urlencode(params))


def get_uid(results):
    results = dict(results)

    args = {
        'openid.assoc_handle': results['openid.assoc_handle'][0],
        'openid.signed': results['openid.signed'][0],
        'openid.sig': results['openid.sig'][0],
        'openid.ns': results['openid.ns'][0]
    }

    s_args = results['openid.signed'][0].split(',')

    for arg in s_args:
        arg = 'openid.{0}'.format(item)
        if results[arg][0] not in args:
            args[arg] = results[arg][0]

    args['openid.mode'] = 'check_authentication'

    request = requests.post(STEAM_LOGIN_URL, args)
    request.connection.close()

    if re.search('is_valid:true', request.text):
        uid_re = re.search('https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'][0])
        if uid_re or uid_re.group(1) != None:
            return uid_re.group(1)
        else:
            return False
    else:
        return False

def RedirectToSteamSignIn(response_url, use_ssl):
    import sys
    print >> sys.stdout, "Warning! `RedirectToSteamSignIn` and `GetSteamID64` methods are DEPRECATED. Please use `auth` and `get_uid` instead."
    return auth(response_url, use_ssl)

def GetSteamID64(results):
    import sys
    print >> sys.stdout, "Warning! `RedirectToSteamSignIn` and `GetSteamID64` methods are DEPRECATED. Please use `auth` and `get_uid` instead."
    return get_uid(results)