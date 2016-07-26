import requests

WIGLE_ENDPOINT = 'https://wigle.net/api/v1'

# How many entries will be sent from the server at one time. This is hardcoded
# on the website.
WIGLE_PAGESIZE = 100


def normalise_entry(net):
    net['trilat'] = float(net['trilat'])
    net['trilong'] = float(net['trilong'])


class WigleError(Exception):
    pass


class WigleAuthenticationError(WigleError):
    """
    Incorrect credentials.
    """
    pass


class WigleRequestFailure(WigleError):
    """
    Generic "request unsuccessful" error.
    """
    pass


class WigleRatelimitExceeded(WigleRequestFailure):
    """
    Too many requests have been made in a short time.
    """
    pass


def raise_wigle_error(data):
    message = data.get('message')
    if message == "too many queries":
        raise WigleRatelimitExceeded()
    else:
        raise WigleRequestFailure(message)

class Wigle(object):
    def __init__(self, user, password):
        """
        Create a new webservice proxy object. It will authenticate with user
        and password credentials on the first connection attempt.
        """
        self.user = user
        self.password = password
        self._auth_cookies = None

    def _wigle_request(self, method, auth=False, **kwargs):
        url = WIGLE_ENDPOINT + '/' + method
        if auth:
            cookies = self._auth_cookies
        else:
            cookies = None
        headers = {
            'Accept': 'application/json, text/javascript',
            'User-Agent': 'python wigle client',
            'Content-Type': 'application/json',
            }
        return requests.post(url, cookies=cookies, headers=headers, **kwargs)

    def _authenticated_request(self, method, **kwargs):
        self._ensure_authenticated()
        return self._wigle_request(method, auth=True, **kwargs)

    def _unauthenticated_request(self, method, **kwargs):
        return self._wigle_request(method, auth=False, **kwargs)

    def reauthenticate(self):
        self._auth_cookies = None
        auth_data = {
            'credential_0': self.user,
            'credential_1': self.password,
            'noexpire': 'off',
            'destination': '/',
        }
        resp = self._unauthenticated_request('jsonLogin', params=auth_data, allow_redirects=False)
        if 'auth' in resp.cookies:
            self._auth_cookies = resp.cookies
        else:
            raise WigleAuthenticationError('Could not authenticate as user %s' % self.user)

    def _ensure_authenticated(self):
        if not self._auth_cookies:
            self.reauthenticate()

    def get_user_info(self):
        """
        Request information about current user.

        Returns:
            dict: Description of user.
        """
        resp = self._authenticated_request('jsonUser')
        info = resp.json()
        return info


    def from_coordinates(self, lat, lon, lat_off = 0.000944, lon_off = 0.001148):
        return self.search(lat_range=(lat - lat_off, lat + lat_off), 
                            long_range = (lon - lon_off, lon + lon_off))
    

    def search(self, lat_range=None, long_range=None, variance=None,
               bssid=None, ssid=None,
               last_update=None,
               address=None, state=None, zipcode=None,
               on_new_page=None, max_results=100):
        """
        Search the Wigle wifi database for matching entries. The following
        criteria are supported:

        Args:
            lat_range ((float, float)): latitude range
            long_range ((float, float)): longitude range
            variance (float): radius tolerance in degrees
            bssid (str): BSSID/MAC of AP
            ssid (str): SSID of network
            last_update (datetime): when was the AP last seen
            address (str): location, address
            state (str): location, state
            zipcode (str): location, zip code
            on_new_page (func(int)): callback to notify when requesting new
                page of results

        Returns:
            [dict]: list of dicts describing matching wifis
        """

        params = {
            'latrange1': lat_range[0] if lat_range else "",
            'latrange2': lat_range[1] if lat_range else "",
            'longrange1': long_range[0] if long_range else "",
            'longrange2': long_range[1] if long_range else "",
            'variance': str(variance) if variance else "0.01",
            'netid': bssid or "",
            'ssid': ssid or "",
            'lastupdt': last_update.strftime("%Y%m%d%H%M%S") if last_update else "",
            'addresscode': address or "",
            'statecode': state or "",
            'zipcode': zipcode or "",
            'Query': "Query",
        }

        # to test:
        wifis = [{u'comment': None, u'qos': u'1', u'name': None, u'netid': u'1C:B0:94:7D:C5:E0', u'personid': u'63434', u'trilong': -122.13879395, u'lastupdt': u'20141030121938', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'?', u'flags': None, u'bcninterval': None, u'trilat': 37.45294952, u'firsttime': u'2014-06-22 14:53:00', u'transid': u'20140622-00407', u'lasttime': u'2014-10-30 14:17:29', u'type': u'????', u'channel': None, u'ssid': None}, {u'comment': None, u'qos': u'4', u'name': None, u'netid': u'00:1e:c7:64:a6:81', u'personid': u'36998', u'trilong': -122.13832092, u'lastupdt': u'20111105180912', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': None, u'bcninterval': None, u'trilat': 37.45297241, u'firsttime': u'2009-07-20 23:42:09', u'transid': u'20090725-00057', u'lasttime': u'2011-11-05 20:09:07', u'type': u'infra', u'channel': u'1', u'ssid': u'2WIRE885'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:16:b6:14:c6:d0', u'personid': u'36998', u'trilong': -122.13994598, u'lastupdt': u'20090725214211', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': None, u'bcninterval': None, u'trilat': 37.45326233, u'firsttime': u'2009-07-20 23:42:59', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:11', u'type': u'infra', u'channel': u'8', u'ssid': u'linksys1452'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:0d:93:7f:0d:0d', u'personid': u'36998', u'trilong': -122.14028168, u'lastupdt': u'20090725214233', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': None, u'bcninterval': None, u'trilat': 37.45338821, u'firsttime': u'2009-07-20 23:43:04', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:33', u'type': u'infra', u'channel': u'1', u'ssid': u'Apple Network 7f0d0d'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:12:17:3f:1e:05', u'personid': u'36998', u'trilong': -122.14028168, u'lastupdt': u'20090725214209', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': None, u'bcninterval': None, u'trilat': 37.45338821, u'firsttime': u'2009-07-20 23:42:54', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:09', u'type': u'infra', u'channel': u'6', u'ssid': u'the2arnolds'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:13:10:0e:38:37', u'personid': u'36998', u'trilong': -122.14028168, u'lastupdt': u'20090725214217', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': None, u'bcninterval': None, u'trilat': 37.45338821, u'firsttime': u'2009-07-20 23:43:04', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:17', u'type': u'infra', u'channel': u'6', u'ssid': u'OLSON'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:18:39:7a:cf:cf', u'personid': u'36998', u'trilong': -122.14028168, u'lastupdt': u'20090725214213', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': None, u'bcninterval': None, u'trilat': 37.45338821, u'firsttime': u'2009-07-20 23:43:04', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:13', u'type': u'infra', u'channel': u'8', u'ssid': u'fishy'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:18:4d:96:b7:50', u'personid': u'36998', u'trilong': -122.14028168, u'lastupdt': u'20090725214216', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': None, u'bcninterval': None, u'trilat': 37.45338821, u'firsttime': u'2009-07-20 23:42:39', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:16', u'type': u'infra', u'channel': u'6', u'ssid': u'Blinky'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1e:58:34:a5:59', u'personid': u'36998', u'trilong': -122.14046478, u'lastupdt': u'20090725214221', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': None, u'bcninterval': None, u'trilat': 37.45345306, u'firsttime': u'2009-07-20 23:43:04', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:21', u'type': u'infra', u'channel': u'6', u'ssid': u'Wayne'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1e:c7:00:0c:89', u'personid': u'36998', u'trilong': -122.14046478, u'lastupdt': u'20090725214221', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': None, u'bcninterval': None, u'trilat': 37.45345306, u'firsttime': u'2009-07-20 23:43:09', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:21', u'type': u'infra', u'channel': u'10', u'ssid': u'2WIRE328'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:24:36:ab:ca:1f', u'personid': u'36998', u'trilong': -122.14046478, u'lastupdt': u'20090725214232', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': None, u'bcninterval': None, u'trilat': 37.45345306, u'firsttime': u'2009-07-20 23:42:44', u'transid': u'20090725-00057', u'lasttime': u'2009-07-25 23:42:32', u'type': u'infra', u'channel': u'2', u'ssid': u'Apple Network abca20'}, {u'comment': None, u'qos': u'7', u'name': None, u'netid': u'00:3A:98:F1:A0:40', u'personid': u'63434', u'trilong': -122.14038086, u'lastupdt': u'20151017161222', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'2', u'flags': None, u'bcninterval': None, u'trilat': 37.45371246, u'firsttime': u'2011-11-30 05:12:28', u'transid': u'20111129-00424', u'lasttime': u'2015-10-17 16:12:11', u'type': u'infra', u'channel': u'1', u'ssid': u'WirelessICC'}, {u'comment': None, u'qos': u'2', u'name': None, u'netid': u'00:18:39:0c:09:0e', u'personid': u'32172', u'trilong': -122.13853455, u'lastupdt': u'20110721004919', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45400238, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2011-07-21 02:37:01', u'type': u'infra', u'channel': u'6', u'ssid': u'cottage'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:15:c6:06:dd:10', u'personid': u'32172', u'trilong': -122.13853455, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45401764, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'9', u'ssid': u'pantry'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1e:e5:a2:a0:31', u'personid': u'32172', u'trilong': -122.1386261, u'lastupdt': u'20081006191356', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.4540329, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:56', u'type': None, u'channel': u'1', u'ssid': u'Basement'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:18:39:6e:5b:b0', u'personid': u'32172', u'trilong': -122.13874054, u'lastupdt': u'20081006191356', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'50', u'trilat': 37.45405197, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:56', u'type': None, u'channel': u'1', u'ssid': u'Acura'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:13:46:cc:60:c2', u'personid': u'32172', u'trilong': -122.13864136, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': u'0001', u'bcninterval': u'100', u'trilat': 37.45405579, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'6', u'ssid': u'default'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1b:5b:f5:c1:21', u'personid': u'32172', u'trilong': -122.13868713, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45406723, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'10', u'ssid': u'NGUYEN'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:15:c6:28:89:70', u'personid': u'32172', u'trilong': -122.13912201, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45418167, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'9', u'ssid': u'closet'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:18:39:ba:04:1b', u'personid': u'32172', u'trilong': -122.13915253, u'lastupdt': u'20081006191356', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45419693, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:56', u'type': None, u'channel': u'1', u'ssid': u'z'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1c:10:8e:78:29', u'personid': u'32172', u'trilong': -122.13950348, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45442581, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'1', u'ssid': u'Sundance'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1d:7e:4e:51:e5', u'personid': u'32172', u'trilong': -122.13952637, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45444107, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'6', u'ssid': u'1450linksys'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:12:17:aa:91:32', u'personid': u'32172', u'trilong': -122.13961792, u'lastupdt': u'20081006191354', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.45450211, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:54', u'type': None, u'channel': u'6', u'ssid': u'linksys_SES_34994'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:1a:70:ab:49:15', u'personid': u'32172', u'trilong': -122.13969421, u'lastupdt': u'20081006191355', u'freenet': u'?', u'paynet': u'?', u'userfound': False, u'visible': u'Y', u'wep': u'Y', u'flags': u'0021', u'bcninterval': u'100', u'trilat': 37.4545517, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:55', u'type': None, u'channel': u'1', u'ssid': u'Sundance'}, {u'comment': None, u'qos': u'0', u'name': None, u'netid': u'00:0f:cc:f2:05:6c', u'personid': u'32172', u'trilong': -122.13981628, u'lastupdt': u'20081006191356', u'freenet': u'?', u'paynet': u'Y', u'userfound': False, u'visible': u'Y', u'wep': u'N', u'flags': u'0001', u'bcninterval': u'100', u'trilat': 37.45462799, u'firsttime': u'0000-00-00 00:00:00', u'transid': u'20081006-00024', u'lasttime': u'2008-10-06 21:13:56', u'type': None, u'channel': u'6', u'ssid': u'Netopia'}]

       
        return wifis


        wifis = []
        while True:
            if on_new_page:
                on_new_page(params.get('first', 1))
            resp = self._authenticated_request('jsonSearch', params=params)
            
            data = resp.json()
            if not data['success']:
                raise_wigle_error(data)

            for result in data['results'][:max_results-len(wifis)]:
                normalise_entry(result)
                wifis.append(result)

            if data['resultCount'] < WIGLE_PAGESIZE or len(wifis) >= max_results:
                break

            params['first'] = data['last'] + 1

        return wifis

