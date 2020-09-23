import requests
import re

from core.services.git_formatters import GitHubFormatter, GitLabFormatter, BitBucketFormatter

# TODO: remake by djanggo.http.requests ?

KNOWN_PROVIDERS = {
    'github.com': {
        'parser': GitHubFormatter,
        'access': {"Authorization": "Basic bWVvb29rOmozMjYybmV3"},
    },
    'bitbucket.org': {
        'parser': BitBucketFormatter,
        # 'access': {"Authorization": "Basic bWVva29rOmozWVVLY3o0VlduSktFNG5ONk1x"},
        # 'access': {"Authorization": "Bearer 0WlTc1M5xvoQyP2iAlngD4FC"},
        'access': {},
        # 'access': {"Authorization": "JWT mljGwCcMuMf9TLMQC6DJFEAD"},
    },
    'gitlab.com': {
        'parser': GitLabFormatter,
        'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
    }
}
REPO_CHECK_KEYS = ('provider', 'owner', 'name', 'path', 'branch', 'hash', 'access')


class GitManage:
    """ Class to work with git repositories - GitHub, GitLab, BitBucket (file_manager and folder_manager subclass) """

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
        return self.__git.url_create(self.__repo, filename)

    def __request(self, link, as_file=False):
        """ Check url and return JSON  """
        access = self.__repo['access'] if self.__repo['access'] else KNOWN_PROVIDERS[self.__repo['provider']]['access']
        headers = {**self.__git.headers, **access}
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
        repo_hash, err = self.__request(self.url)
        if repo_hash:
            self.__sha = repo_hash
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
            return self.__update_files(file_list)
        return False

    def __update_files(self, file_list):
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

    def upload_file(self, path, git_name, git_hash=None):
        """ Upload file to git repository """
        if not self.__object_check:
            return False
        print('START UPLOAD', path, git_name)
        access = self.__repo['access'] if self.__repo['access'] else KNOWN_PROVIDERS[self.__repo['provider']]['access']
        try:
            with open(path, 'rb') as filo:
                values = (self.__repo, access, git_name, git_hash, filo.read())
                request_obj = self.__git.request_obj_for_file_upload(*values)
                print('REQUEST URL', request_obj['url'])
        except FileNotFoundError:
            self.__error = f'Translated copy "{path}" not found'
        else:
            # print('REQUEST DATA', request_obj['params'])
            print('REQUEST DATA', request_obj)
            with requests.request(**request_obj) as resp:
                print('CODE', resp.status_code)
                print('HEADER R', resp.request.headers)
                if resp.status_code < 300:
                    print('ANSWER', resp.json())
                    return self.__git.hash_from_resp_upload(resp)
                print('RESPONSE ERR', self.__git.error_from_resp(resp))
        return False

    @staticmethod
    def __download_file(filo, download_url):
        """ Download file from git repository """
        # NOTE the stream=True parameter below
        with requests.get(download_url, stream=True) as r:
            if r.status_code == requests.codes.ok:
                r.raise_for_status()
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


