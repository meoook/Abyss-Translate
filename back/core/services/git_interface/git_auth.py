import base64
from core.services.git_interface.git_util import GitProviderUtils
from django.conf import settings

# TODO: Key to env


class OAuth2Token:
    """ Util to get refresh token (main idea to pass provider class creation) """
    def __init__(self, git_obj, code=None):
        self.__set_provider(git_obj['provider'])
        self.__code = code

    def __repr__(self):
        if self.__code and self.__connector:
            return self.__connector.get_refresh_token(self.__code)
        return ''

    def __set_provider(self, provider):
        self.__connector = None
        if provider == 'github.com':
            self.__connector = AuthGitHub()
        elif provider == 'gitlab.com':
            self.__connector = AuthGitLab()
        elif provider == 'bitbucket.org':
            self.__connector = AuthBitBucket()


class AuthConnector:
    """ Auth system for git repositories """
    # TODO: Generate URL for redirect ( provider state parameter )

    def __init__(self, abyss_auth):
        self._abyss_auth = abyss_auth  # {'access_type': '', 'token': ''}

    def get_access_token(self, access_type, token=None):
        """ Get token by type - abyss access if type not defined (abyss account must be registered in git provider) """
        _type, _token = access_type, token
        if not _token or _type not in ['oauth', 'ssh', 'token']:  # Use abyss as default
            _type, _token = self._abyss_auth['access_type'], self._abyss_auth['token']
        if _type == 'oauth':
            return self._oauth_get_access_token_by_refresh(_token)
        return _token  # for token and ssh types

    def get_refresh_token(self, user_code):
        """ Get access token by refresh token (some providers don't have refresh system) """
        return self._oauth_get_refresh_token_by_code(user_code) if user_code else ''

    def get_header(self, access_token):
        """ Auth header for provider """
        raise NotImplementedError('Method get_header not implemented in provider Auth class')

    def _oauth_get_access_token_by_refresh(self, refresh_token):
        """
            Get access token by refresh token.
            Some providers don't have refresh system. For them: token = token
        """
        raise NotImplementedError('Method oauth_get_access_token_by_refresh not implemented in provider Auth class')

    def _oauth_get_refresh_token_by_code(self, user_code):
        """ Get refresh/auth token by user code - this code returned from provider callback OAuth2 """
        raise NotImplementedError('Method oauth_get_refresh_token_by_code not implemented in provider Auth class')

    @staticmethod
    def _basic_auth(app_id, app_secret):
        encoded_credentials = f'{app_id}:{app_secret}'.encode()
        return f'Basic {base64.b64encode(encoded_credentials).decode()}'

    @staticmethod
    def _return_token(req_obj, token_type='access'):
        """ Send request and return token by type """
        response, err = GitProviderUtils.make_request(req_obj)
        if err:
            return ''
        if token_type == 'refresh':
            return response['refresh_token']
        if token_type == 'access':
            return response['access_token']
        return ''


class AuthGitHub(AuthConnector):
    __abyss_auth = {'access_type': 'token', 'token': 'a64a7ef131c0a8823e9f4b8228b86f5c077fd6b9'}
    __oauth_url_redirect = 'https://github.com/login/oauth/authorize'  # scope, state, allow_signup
    __oauth_url_access = 'https://github.com/login/oauth/access_token'
    # __oauth_app_id = '55aa8a87265bfa0f5ccf'
    # __oauth_secret = 'fa43864806ab46c5fb45f39ee8828d110a4d8b59'
    __oauth_app_id = settings.SOCIAL_GITHUB_CLIENT
    __oauth_secret = settings.SOCIAL_GITHUB_SECRET

    # NTVhYThhODcyNjViZmEwZjVjY2Y6ZmE0Mzg2NDgwNmFiNDZjNWZiNDVmMzllZTg4MjhkMTEwYTRkOGI1OQ==

    def __init__(self):
        super().__init__(self.__abyss_auth)

    def get_header(self, access_token):
        return {'Authorization': f'token {access_token}'}

    def _oauth_get_refresh_token_by_code(self, user_code):
        req_obj = {
            'method': 'POST',
            'url': self.__oauth_url_access,
            'headers': {
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            },
            'data': {
                # "grant_type": "authorization_code",
                'code': user_code,
                'client_id': self.__oauth_app_id,
                'client_secret': self.__oauth_secret,
            },
        }
        return self._return_token(req_obj, 'access')  # GitHub don't have refresh token system

    def _oauth_get_access_token_by_refresh(self, refresh_token):
        return refresh_token


class AuthBitBucket(AuthConnector):
    __abyss_auth = {'access_type': 'oauth', 'token': 'dT3cWh4p3QxvMf4WnG'}
    __oauth_url_redirect = 'https://bitbucket.org/site/oauth2/authorize'
    __oauth_url_access = 'https://bitbucket.org/site/oauth2/access_token'
    __oauth_app_id = settings.SOCIAL_BITBUCKET_CLIENT
    __oauth_secret = settings.SOCIAL_BITBUCKET_SECRET
    # __oauth_app_id = 'xckDCgTDkpEAtWnfYe'
    # __oauth_secret = 'TTuaxUvCPynXBZd6pMeumDtfuchzdJvp'

    # eGNrRENnVERrcEVBdFduZlllOlRUdWF4VXZDUHluWEJaZDZwTWV1bUR0ZnVjaHpkSnZw

    def __init__(self):
        super().__init__(self.__abyss_auth)

    def get_header(self, access_token):
        return {'Authorization': f'Bearer {access_token}'}

    def _oauth_get_refresh_token_by_code(self, user_code):
        req_obj = {
            'method': 'POST',
            'url': self.__oauth_url_access,
            'headers': {
                'Cache-Control': 'no-cache',
                'Authorization': self._basic_auth(self.__oauth_app_id, self.__oauth_secret),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            'data': {
                'grant_type': 'authorization_code',
                'code': user_code,
            },
        }
        return self._return_token(req_obj, 'refresh')

    def _oauth_get_access_token_by_refresh(self, refresh_token):
        req_obj = {
            'method': 'POST',
            'url': self.__oauth_url_access,
            'headers': {
                'Cache-Control': 'no-cache',
                'Authorization': self._basic_auth(self.__oauth_app_id, self.__oauth_secret),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            'data': {
                'grant_type': 'refresh_token',
                'refresh_token': f'{refresh_token}',
            },
        }
        return self._return_token(req_obj, 'access')


class AuthGitLab(AuthConnector):
    __abyss_auth = {'access_type': 'token', 'token': 'ZocaYQAp9UYd18wk1Psk'}
    __oauth_url_redirect = 'https://gitlab.com/oauth/authorize'  # state
    __oauth_url_access = 'https://gitlab.com/oauth/access_token'  # /oauth/token
    __oauth_app_id = settings.SOCIAL_GITLAB_CLIENT
    __oauth_secret = settings.SOCIAL_GITLAB_SECRET
    # __oauth_app_id = '56fcf0ae30f04c6d0bfa1a327274eb81a2c3bf6d64f1b5927ac0d2f47ef4ecdf'
    # __oauth_secret = '5ccb384de48b1041d39af4b570afe95281fb8e4a79c3b4382ec3ea7dbffc6309'

    def __init__(self):
        super().__init__(self.__abyss_auth)

    def get_header(self, access_token):
        return {'PRIVATE-TOKEN': f'{access_token}'}

    def _oauth_get_refresh_token_by_code(self, user_code):
        req_obj = {
            'method': 'POST',
            'url': self.__oauth_url_access,
            'headers': {
                'Cache-Control': 'no-cache',
                # 'Authorization': self._basic_auth(self.__oauth_app_id, self.__oauth_secret),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            # redirect_uri must match the redirect_uri used in the original authorization request.
            # 'redirect_uri': 'REDIRECT_URI',
            'data': {
                'grant_type': 'authorization_code',
                'code': user_code,
                'client_id': self.__oauth_app_id,
                'client_secret': self.__oauth_secret,
            },
        }
        return self._return_token(req_obj, 'refresh')

    def _oauth_get_access_token_by_refresh(self, refresh_token):
        req_obj = {
            'method': 'POST',
            'url': self.__oauth_url_access,
            'headers': {
                'Cache-Control': 'no-cache',
                'Authorization': self._basic_auth(self.__oauth_app_id, self.__oauth_secret),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            'data': {
                'grant_type': 'refresh_token',
                'refresh_token': f'{refresh_token}',
            },
        }
        return self._return_token(req_obj, 'access')
