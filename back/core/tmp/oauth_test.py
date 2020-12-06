import base64
import json

import requests


def get_data(token):
    url = "https://api.bitbucket.com/2.0/repositories/mewooook/test/src/master/Folder1"
    # Method 1: Token in auth header (preferred)
    headers = {
        'Cache-Control': 'no-cache',
        'Authorization': f'Bearer {token}',
        'Accept': '*/*',
    }
    params = {'format': 'meta'}
    print(headers)
    response = requests.request("GET", url, headers=headers, params=params)
    print('METHOD 1:', response.text)

    # Method 3: Token in URL (security warning)
    params2 = {
        'format': 'meta',
        'access_token': token
    }
    headers = {
        'Cache-Control': 'no-cache',
        # 'Authorization': f'Bearer {token}',
        'Accept': '*/*',
    }
    response2 = requests.request("GET", url, headers=headers, params=params2)
    print('METHOD 3:', response2.text)

    response.close()
    response2.close()


req_obj = {
    "method": "POST",
    "url": "https://bitbucket.org/site/oauth2/access_token",
    "headers": {
        "Cache-Control": "no-cache",
        "Authorization": "Basic eGNrRENnVERrcEVBdFduZlllOlRUdWF4VXZDUHluWEJaZDZwTWV1bUR0ZnVjaHpkSnZw",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    "data": {
        "grant_type": "refresh_token",
        "refresh_token": "dT3cWh4p3QxvMf4WnG"
    }
}

with requests.request(**req_obj) as req:
    if req.status_code < 300:
        data = req.json()
        print('JSON IS', data)
        token = data['access_token']
        print('token', token)
        get_data(token)
    else:
        print('ERRR', req.text)

