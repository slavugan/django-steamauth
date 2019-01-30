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
    args = {
        'openid.assoc_handle': results['openid.assoc_handle'],
        'openid.signed': results['openid.signed'],
        'openid.sig': results['openid.sig'],
        'openid.ns': results['openid.ns']
    }

    for s_arg in results['openid.signed'].split(','):
        arg = 'openid.{0}'.format(s_arg)
        if arg not in args:
            args[arg] = results[arg]

    args['openid.mode'] = 'check_authentication'

    request = requests.post(STEAM_LOGIN_URL, args)
    request.connection.close()

    if re.search('is_valid:true', request.text):
        uid_re = re.search('https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'])
        if uid_re and uid_re.lastindex > 0:
            return uid_re.group(1)
