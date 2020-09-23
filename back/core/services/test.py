# import base64
#
# usr = 'localize:rkPVAewgjaaK4qCbNmLh'
# usr2 = 'mewooook@gmail.com:lkwpeter'
# usr3 = 'mewooook:lkwpeter'
#
# # print(base64.b64encode(b'localize:rkPVAewgjaaK4qCbNmLh').decode())
# # print(base64.b64encode(usr.encode()).decode())
# # print(base64.b64encode(usr2.encode()).decode())
# # print(base64.b64encode(usr3.encode()).decode())
#
#
# print('============================')
# print(base64.b64encode('meokok:j3YUKcz4VWnJKE4nN6Mq'.encode()).decode())
# print(base64.b64encode('api:j3YUKcz4VWnJKE4nN6Mq'.encode()).decode())
# print(base64.b64encode('meokok:lkwpeter'.encode()).decode())
# # print('bWVvb29rOmozMjYybmV3')
#
# aa = True
#
#
# def __decor(function):
#     def test_func(*args, **kwargs):
#         if aa:
#             function(*args, **kwargs)
#         else:
#             print('Error')
#
#     return test_func
#
#
# @__decor
# def test(xx):
#     print(f'test data {xx}')
#
#
# test('bb')
#

import requests


url = 'https://bitbucket.org/site/oauth2/authorize'
url2 = 'https://bitbucket.org/site/oauth2/access_token'
username = 'meokok'
password = 'lkwpeter'

headers = {
    "Accept": "application/json",
    'Content-Type': 'application/x-www-form-urlencoded',
    # "Authorization": "Basic e4dbc97009fa5a1fe77077b127c241e3cb0823a773867be2d7c1c6299fd9fc52"
}
r = requests.post(url, auth=(username, password), params={})
print('HEADERS A', r.request.headers)
print('CONTENT', r.content)
# print('TEXT', r.text)
