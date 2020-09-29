# import base64
# import json
#
import base64

import requests
#
#
# provider = {
#   "consumerKey": "xckDCgTDkpEAtWnfYe",
#   "consumerSecret": "TTuaxUvCPynXBZd6pMeumDtfuchzdJvp",
#   "bitbucketAuthorizeUrl": "https://bitbucket.org/site/oauth2/authorize",
#   "bitbucketAccessTokenUrl": "https://bitbucket.org/site/oauth2/access_token"
# }
#
# #
# # usr = 'localize:rkPVAewgjaaK4qCbNmLh'
# # usr2 = 'mewooook@gmail.com:lkwpeter'
# # usr3 = 'mewooook:lkwpeter'
# #
# # # print(base64.b64encode(b'localize:rkPVAewgjaaK4qCbNmLh').decode())
# # # print(base64.b64encode(usr.encode()).decode())
# # # print(base64.b64encode(usr2.encode()).decode())
# # # print(base64.b64encode(usr3.encode()).decode())
# #
#
# req_obj = {
#     "method": "POST",
#     "url": "https://bitbucket.org/site/oauth2/access_token",
#     "headers": {
#         "Cache-Control": "no-cache",
#         "Authorization": "Basic eGNrRENnVERrcEVBdFduZlllOlRUdWF4VXZDUHluWEJaZDZwTWV1bUR0ZnVjaHpkSnZw",
#         "Content-Type": "application/x-www-form-urlencoded"
#     },
#     "params": json.dumps({
#         "grant_type": "authorization_code",
#         "code": "dg9jH6BPExenx4MWKa"
#     })
# }
#
# r = requests.request(**req_obj)
# print('HEADERS A', r.request.headers)
# print('CONTENT', r.content)
# print('JSON', r.json())
# # print('TEXT', r.text)
# from urllib import parse
#
# print(parse.quote_plus(f'mewooook/testproject'))
#
# url = 'https://api.github.com/repos/meoook/testrepo1/contents/test.txt?ref=master'
# headers = {'Authorization': 'Basic bWVvb29rOmozMjYybmV3'}  # , 'Accept': 'application/vnd.github.v3.object'}
#
# with requests.request('HEAD', url, headers=headers) as req:
#     print('HEADER IS', req.headers.get('ETag').split('"')[1])
#
#
# aaa = {'aa': 'aa', 'bb': {'bb':'bb', 'cc':'dddddd'}}
#
#
# def xaxa(val, fn):
#     print(fn(val))
#
#
# def fun(x):
#     return x['bb']['cc']
#
#
# xaxa(aaa, fun)


cc = base64.b64decode('eGNrRENnVERrcEVBdFduZlllOlRUdWF4VXZDUHluWEJaZDZwTWV1bUR0ZnVjaHpkSnZw')

print(cc)
