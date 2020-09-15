import json
from urllib import parse
import base64

# ABYSS_ACCESS_GITHUB = 'meoook', 'j3262new'


class GitParser:
    """ Basic class structure for git parser """

    def __init__(self, root, repo, file):
        self.__url_root = root
        self.__url_suffix_repo = repo
        self.__url_suffix_file = file

    @property
    def headers(self):
        return {'Content-type': 'application/json'}

    @property
    def _url_folder_format(self):
        """ Return format to create folders or projects request URLs """
        return self.__url_root + self.__url_suffix_repo

    @property
    def _url_file_format(self):
        """ Return format to create file request URLs """
        return self.__url_root + self.__url_suffix_file

    @property
    def _url_upload_format(self):
        return self.__url_root + self.__url_suffix_file

    def url_create(self, git_obj, as_file=False):
        """ Create URL from format """
        if as_file:
            return self._url_file_format.format(**git_obj)
        return self._url_folder_format.format(**git_obj)

    @staticmethod
    def data_from_resp(response, as_file=False):
        """ Return hash and download URL from json response """
        return None, 'Error parsing response with code 200'

    @staticmethod
    def error_from_resp(response):
        """ Return error text from json response """
        try:
            response = response.json()
            return response["message"] if "message" in response else "Unknown response"
        except (KeyError, TypeError):
            return 'Error parsing response with error code'

    def request_obj_for_file_upload(self, git_obj, git_name, data, access):
        """ Create full request object with url, headers, and data """
        path = f'{git_obj["path"]}/{git_name}' if git_obj['path'] else git_name
        link = self._url_upload_format.format(**{**git_obj, 'path': path})
        head = {**access, 'Accept': 'application/vnd.github.v3+json', 'Content-type': 'application/json'}
        data_coded = base64.b64encode(data).decode('utf-8')
        obj = {
            'message': 'Create new file via GitHub API',
            'content': data_coded,
            'branch': git_obj['branch'],
        }
        return {'url': link, 'headers': head, 'data': json.dumps(obj)}


class GitHubParser(GitParser):
    def __init__(self):
        root = 'https://api.github.com/repos/{owner}/{name}'
        repo = '/contents/{path}?ref={branch}'
        file = '/contents/{path}?ref={branch}'
        super().__init__(root, repo, file)

    @property
    def headers(self):
        return {'Accept': 'application/vnd.github.VERSION.object', }

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['sha'], base64.b64decode(response['content'])
            return response['sha'], None
        except (KeyError, TypeError):
            return None, 'Error parsing response with code 200'


class BitBucketParser(GitParser):
    def __init__(self):
        root = 'https://api.bitbucket.com/2.0/repositories/{owner}/{name}'
        repo = '/src/{branch}/{path}?format=meta'  # '/commit/{branch}'
        file = '/src/{branch}/{path}?format=meta'
        super().__init__(root, repo, file)

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['commit']['hash'], response['links']['self']['href']
            return response['commit']['hash'], None
        except (KeyError, TypeError):
            return None, 'Error parsing response with code 200'

    @staticmethod
    def error_from_resp(response):
        code = response.status_code
        if code == 404:
            return 'Not Found'
        elif code == 500:
            return "Error request"
        else:
            return f"Unknown response {code}"


class GitLabParser(GitParser):
    def __init__(self):
        root = 'https://gitlab.com/api/v4/projects/{owner_name}/repository/'
        repo = 'commits?ref_name={branch}&path={path}'
        file = 'files/{path}?ref={branch}'
        super().__init__(root, repo, file)

    def url_create(self, git_obj, as_file=False):
        """ Create URL from format """
        git_obj['owner_name'] = parse.quote_plus(f'{git_obj["owner"]}/{git_obj["name"]}')
        git_obj['path'] = parse.quote_plus(git_obj['path'])
        if as_file:
            return self._url_file_format.format(**git_obj)
        return self._url_folder_format.format(**git_obj)

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['blob_id'], base64.b64decode(response['content'])
            return response[0]['id'], None
        except (KeyError, TypeError):
            return None, 'Error parsing response with code 200'


# USE IN TESTS

# import requests
# if __name__ == '__main__':
#
#     repos = [
#         {
#             'parser': GitHubParser, 'owner': 'meoook', 'name': 'testrepo1',
#             'branch': 'master', 'path': 'Test', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Accept': 'application/vnd.github.VERSION.object'},
#         },
#         {
#             'parser': GitHubParser, 'owner': 'meoook', 'name': 'testrepo1',
#             'branch': 'master', 'path': 'Test/new.txt', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Accept': 'application/vnd.github.VERSION.object'},
#         },
#         {
#             'parser': GitLabParser, 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
#         },
#         {
#             'parser': GitLabParser, 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1/_csv', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
#         },
#         {
#             'parser': BitBucketParser, 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Content-type': 'application/json'},
#         },
#         {
#             'parser': BitBucketParser, 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1/csv.txt', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Content-type': 'application/json'},
#         },
#     ]
#
#     for repo in repos:
#         git = repo["parser"]()
#         url = git.url_create(repo, as_file=repo["as_file"])
#         print('url', url)
#         resp = requests.get(url, headers=repo['access'])
#         if resp.status_code == requests.codes.ok:
#             print(git.data_from_resp(resp, as_file=repo["as_file"]))
#         else:
#             print(git.error_from_resp(resp))
