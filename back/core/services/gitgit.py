import requests
import base64
import re

from core.services.git_parsers import GitHubParser, GitLabParser, BitBucketParser

# TODO: remake by djanggo.http.requests ?
# TODO: upload files

KNOWN_PROVIDERS = {
    'github.com': {
        'parser': GitHubParser,
        'access': {"Authorization": "Basic bWVvb29rOmozMjYybmV3"},
    },
    'bitbucket.org': {
        'parser': BitBucketParser,
        'access': {"Authorization": "Basic bWVvb29rOmozMjYybmV3"},
    },
    'gitlab.com': {
        'parser': GitLabParser,
        'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
    }
}
REPO_CHECK_KEYS = ('provider', 'owner', 'name', 'path', 'branch', 'hash', 'access')


class GitManage:
    def __init__(self):
        self.__repo = None
        self.__sha = None   # hash is in py function
        self.__git = None
        self.__error = None
        self.__url = None

    @property
    def error(self):
        return self.__error

    @property
    def repo(self):
        """ To get repo object from parsed URL """
        return self.__repo

    @repo.setter
    def repo(self, value):
        """ Init repository object """
        self.__repo = None
        self.__sha = None
        self.__git = None
        self.__error = None
        self.__url = None
        if not isinstance(value, dict) and not all(k in REPO_CHECK_KEYS for k in value):
            self.__error = 'Not a valid repository object'
        elif value['provider'] not in KNOWN_PROVIDERS:
            self.__error = f'Git provider {value["provider"]} not configured'
        else:
            self.__repo = value
            self.__git = KNOWN_PROVIDERS[value['provider']]['parser']()
            self.__url = self.__api_url_create()

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, link):
        """ Create repository object from URL """
        # FIXME: folder names with special chars
        assert isinstance(link, str)
        url_items = re.match(r'^http[s]?://([^/]+)/(\w+)/(\w+)(?:/(?:tree|src|-/tree)/(\w+)/?)?(.+)?', link)
        if url_items:
            self.repo = {
                'provider': url_items.group(1), 'owner': url_items.group(2), 'name': url_items.group(3),
                'branch': url_items.group(4) if url_items.group(4) else 'master',
                'path': self.__path_fix(url_items.group(5)) if url_items.group(5) else '',
                'hash': None, 'access': None,
            }
        else:
            self.__error = f'Repo URL parse error: {link}'

    @property
    def sha(self):
        """ Repository object new hash """
        if self.__object_check and self.__sha or self.__repository_connect():
            return self.__sha
        return False

    @property
    def need_update(self):
        """ Repository object update status """
        if self.sha and self.__sha != self.__repo['hash']:
            return True
        return False

    @property
    def __object_check(self):
        """ Function to check object """
        if self.error:
            return False
        elif not self.repo:
            self.__error = 'Repository object not set'
            return False
        return True

    def __api_url_create(self, filename=None):
        """ Builder for API URLs by provider """
        repo = {**self.__repo}
        if filename:
            repo['path'] = f'{repo["path"]}/{filename}' if repo['path'] else filename
        return self.__git.url_create(repo, bool(filename))

    def __request(self, link, as_file=False):
        """ Check url and return JSON  """
        access = self.__repo['access'] if self.__repo['access'] else KNOWN_PROVIDERS[self.__repo['provider']]['access']
        headers = {**self.__git.headers, **access, 'Content-type': 'application/json'}
        with requests.get(link, headers=headers) as resp:
            if resp.status_code == requests.codes.ok:
                return self.__git.data_from_resp(resp, as_file=as_file)
        return None, f'Connect {link} error: {self.__git.error_from_resp(resp)}'

    def __repository_connect(self):
        """ Check access and exist status and set hash for repository object """
        if not self.__git:
            self.__error = f'Git provider not set'
            return False
        # Check connect
        hash, err = self.__request(self.url)
        if hash:
            self.__sha = hash
            return True
        self.__error = err
        return False

    def update_files(self, file_list):
        """ Return file_list with new hash and error field for each file after check and update try """
        if not self.__object_check:
            pass
        elif not isinstance(file_list, list):
            self.__error = 'Params error - need list of file objects'
        else:
            return self.__check_files(file_list)
        return False

    def __check_files(self, file_list):
        """ Get new hash and data or download URL for files in list """
        return_arr = []
        for file_item in file_list:
            add_item = {**file_item, 'err': '', 'updated': False}
            link = self.__api_url_create(add_item["name"])
            file_hash, options = self.__request(link, as_file=True)
            if not file_hash:
                add_item['err'] = options
            elif file_hash != add_item['hash']:
                saved = self.__save_file(add_item['path'], options)
                if saved == 'success':
                    add_item['updated'] = True
                else:
                    add_item['err'] = saved
            add_item['hash'] = file_hash
            return_arr.append(add_item)
        self.__error = None  # Error set for each file but no need to repo object
        return return_arr

    def __save_file(self, path, data):
        """ Download and update status/new_hash for files in list """
        # TODO: Exceptions
        with open(path, 'wb') as filo:
            if data[:5] == 'https':
                self.__download_file(filo, data)
                # except requests.exceptions.ConnectionError:
            else:
                filo.write(data)
        return 'success'

    def upload_file(self, path, git_name):
        """ Upload file to git repository """
        if not self.__object_check:
            return False
        print(path, git_name)
        access = self.__repo['access'] if self.__repo['access'] else KNOWN_PROVIDERS[self.__repo['provider']]['access']
        with open(path, 'rb') as filo:
            request_obj = self.__git.request_obj_for_file_upload(self.__repo, git_name, filo.read(), access)
            print('REQ OBJ', request_obj)
        with requests.delete(**request_obj) as resp:
            print('CODE', resp.status_code)
            print('RESPONSE', resp.json())
            if resp.status_code == requests.codes.ok:
                return True
        return False

    @staticmethod
    def __download_file(filo, download_url):
        """ Download file from git repository """
        # NOTE the stream=True parameter below
        with requests.get(download_url, stream=True) as r:
            if r.status_code == requests.codes.ok:
                # r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    filo.write(chunk)

    @staticmethod
    def __path_fix(full_path):
        """ Remove filename from path if it's found """
        path_items = re.match(r'^(.+)/(?:[^/\s]+\.[^/\s]+)?$', full_path)
        return path_items.group(1) if path_items else full_path


# USE IN TESTS

if __name__ == '__main__':

    repos = [
        {
            'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
            'branch': 'master', 'path': 'Test',
            'hash': None, 'access': None,
            'file_list': [
                {'path': 'C:/tmp/error_github.txt', 'name': 'new.txt', 'hash': '6d1280d85312042a9a3964bf2e34382a999e171b'},
                {'path': 'C:/tmp/test_file_github.txt', 'name': 'test_file.txt', 'hash': ''},
                {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': ''},
            ],
        },
#         {
#             'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
#             'branch': 'master', 'path': 'Test',
#             'hash': '35646d4053e5cea51fd560f63fc98a2298e77e48', 'access': None,
#             'file_list': [
#                 {'path': 'C:/tmp/error_github.txt', 'name': 'new.txt', 'hash': ''},
#                 {'path': 'C:/tmp/err_github.txt', 'name': 'test_file.txt', 'hash': '2ef267e25bd6c6a300bb473e604b092b6a48523b'},
#
#             ],
#         },
#         {
#             'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1',
#             'hash': None, 'access': None,
#             'file_list': [
#                 {'path': 'C:/tmp/error_gitlab.txt', 'name': '_csv.txt', 'hash': '6b882514cbadfceb1775a0347ffa2d321e7b8297'},
#                 {'path': 'C:/tmp/test_file_gitlab.txt', 'name': 'test_file.txt', 'hash': ''},
#                 {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': ''},
#             ],
#         },
#         {
#             'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1',
#             'hash': '72930c112a2a1b3e634321cf107192fc85106081', 'access': None,
#             'file_list': [
#                 {'path': 'C:/tmp/error_github.txt', 'name': '_csv.txt', 'hash': ''},
#                 {'path': 'C:/tmp/err_github.txt', 'name': 'test_file.txt', 'hash': '54d622dd730f79aa5b8d2582bb5fb2cc6f92bfa4'},
#
#             ],
#         },
#         {
#             'provider': 'bitbucket.org', 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1',
#             'hash': None, 'access': None,
#             'file_list': [
#                 {'path': 'C:/tmp/error_bitbucket.txt', 'name': 'csv.txt', 'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa'},
#                 {'path': 'C:/tmp/test_file__bitbucket.txt', 'name': 'test_file.txt', 'hash': ''},
#                 {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': ''},
#             ],
#         },
#         {
#             'provider': 'bitbucket.org', 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1',
#             'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa', 'access': None,
#             'file_list': [
#                 {'path': 'C:/tmp/error_bitbucket.txt', 'name': 'csv.txt', 'hash': ''},
#                 {'path': 'C:/tmp/err_bitbucket.txt', 'name': 'test_file.txt', 'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa'},
#             ],
#         },
    ]

    for repo in repos:
        git = GitManage()
        git.repo = repo
        # print('====================================')
        # print(git.url)
        # if git.sha:
        #     print(git.sha)
        #     print('Need update?', git.need_update)
        #     if git.need_update:
        #         updated = git.update_files(repo['file_list'])
        #         [print(x['name'], x['hash'], x['err'], x['updated']) for x in updated]
        # else:
        #     print(git.error)
        print('====================================')
        file_hash = git.upload_file(path=repo['file_list'][1]['path'], git_name='test-en.txt')
        if file_hash:
            print('Success', file_hash)
        else:
            print('Error', git.error)
