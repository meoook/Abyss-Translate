import os
import requests

OAUTH_URLS = {
    'github.com': {
        'auth': 'https://github.com/login/oauth/authorize',        # client_id, redirect_uri, login
        'access': 'https://github.com/login/oauth/access_token',   # scope, state, allow_signup
        'format': lambda access_token: {'Authorization': f'token {access_token}'},
    },
    'bitbucket.org': {
        'auth': 'https://bitbucket.org/site/oauth2/authorize',
        'access': 'https://bitbucket.org/site/oauth2/access_token',
        'format': lambda access_token: {'Authorization': f'Bearer {access_token}'},
        'app_id': 'xckDCgTDkpEAtWnfYe',
        'app_secret': 'TTuaxUvCPynXBZd6pMeumDtfuchzdJvp',
    },
    'gitlab.com': {
        'auth': 'https://gitlab.com/oauth/authorize',               # state
        'access': 'https://gitlab.com/oauth/access_token',
    },
}

# https://example.com/oauth/redirect?code=1234567890&state=YOUR_UNIQUE_STATE_HASH
# https://gitlab.example.com/oauth/authorize?client_id=APP_ID&redirect_uri=REDIRECT_URI&response_type=code&state=YOUR_UNIQUE_STATE_HASH&scope=REQUESTED_SCOPES

class GitOAuth2:
    """ Get access token through OAuth2 (social auth) """

    def __init__(self, provider, app_id, app_secret, refresh_token):
        req_obj = {
            "method": "POST",
            "url": "https://bitbucket.org/site/oauth2/access_token",
            "headers": {
                "Cache-Control": "no-cache",
                "Authorization": "Basic {}".format(bas),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            "data": {
                "grant_type": "authorization_code",
                "code": code,
            },
        }

