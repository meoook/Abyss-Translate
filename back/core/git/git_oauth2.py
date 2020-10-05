import base64
import requests

OAUTH_PROVIDERS = {
    'github.com': {
        'auth': 'https://github.com/login/oauth/authorize',  # client_id, redirect_uri, login
        'access': 'https://github.com/login/oauth/access_token',  # scope, state, allow_signup
        'format': lambda access_token: {'Authorization': f'token {access_token}'},
        'app_id': '55aa8a87265bfa0f5ccf',
        'app_secret': 'fa43864806ab46c5fb45f39ee8828d110a4d8b59',
    },
    'bitbucket.org': {
        'url_auth': 'https://bitbucket.org/site/oauth2/authorize',
        'url_access': 'https://bitbucket.org/site/oauth2/access_token',
        'format': lambda access_token: {'Authorization': f'Bearer {access_token}'},
        'app_id': 'xckDCgTDkpEAtWnfYe',
        'app_secret': 'TTuaxUvCPynXBZd6pMeumDtfuchzdJvp',
    },
    'gitlab.com': {
        'auth': 'https://gitlab.com/oauth/authorize',  # state
        'access': 'https://gitlab.com/oauth/access_token',
    },
}


# https://example.com/oauth/redirect?code=1234567890&state=YOUR_UNIQUE_STATE_HASH
# https://gitlab.example.com/oauth/authorize?client_id=APP_ID&redirect_uri=REDIRECT_URI&response_type=code&state=YOUR_UNIQUE_STATE_HASH&scope=REQUESTED_SCOPES


class GitOAuth2:
    """ Get access token through OAuth2 (social auth) """

    def __init__(self, provider):
        oauth = OAUTH_PROVIDERS[provider]
        self.__url = oauth['url_access']
        self.__basic_auth = oauth["app_id"], oauth["app_secret"]

    @property
    def __basic_auth(self):
        """ App authorization credentials for provider """
        return self.__basic_credentials

    @__basic_auth.setter
    def __basic_auth(self, credentials):
        app_id, app_secret = credentials
        encoded_credentials = f'{app_id}:{app_secret}'.encode()
        self.__basic_credentials = f'Basic {base64.b64encode(encoded_credentials).decode()}'

    def access_token(self, refresh_token):
        """ Get token by refresh token """
        req_obj = {
            'method': 'POST',
            'url': self.__url,
            'headers': {
                'Cache-Control': 'no-cache',
                'Authorization': self.__basic_auth,
            },
            'data': {
                'grant_type': 'refresh_token',
                'refresh_token': f'{refresh_token}',
            }
        }
        response, err = self.__send_request(req_obj)
        if err:
            return None, err
        access_token = response['access_token']
        # refresh_token = response['refresh_token']
        return access_token, None

    def refresh_token(self, user_code):
        """ Get refresh and auth token by user code - this code returned from provider callback OAuth2 """
        if user_code:
            req_obj = {
                "method": "POST",
                "url": self.__url,
                "headers": {
                    "Cache-Control": "no-cache",
                    "Authorization": self.__basic_auth,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                "data": {
                    "grant_type": "authorization_code",
                    "code": user_code,
                },
            }
            response, err = self.__send_request(req_obj)
            if err:
                return None, err
            refresh_token = response['refresh_token']
            return refresh_token, None

    @staticmethod
    def __send_request(request_object):
        """ Handle connection errors """  # FIXME: same method as in git_util class
        err = f'Connect {request_object["url"]} error: '
        try:
            with requests.request(**request_object) as response:
                code = response.status_code
                if code < 300:
                    if not response.text:
                        return response, None
                    try:
                        return response.json(), None
                    except ValueError:
                        return None, 'json parse'
                elif code == 403:
                    return None, err + 'no access'
                elif code == 404:
                    return None, err + 'not found'
                else:
                    print('RESP CODE IS', response.text)
                    return None, err + f'unknown user code {code}'
        except requests.exceptions.ConnectionError:
            return None, err + 'network'


if __name__ == '__main__':
    aa = GitOAuth2('github.org')

    xx = aa.refresh_token('ZYSbgQSrEcAq33NPLx')
    print(xx)
