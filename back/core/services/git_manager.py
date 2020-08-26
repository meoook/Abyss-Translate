import requests
# import base64
import re

# TODO: remake by djanggo.http.requests
# TODO: upload files

KNOWN_PROVIDERS = {
    'github.com': {
        'repo': 'https://api.github.com/repos/{owner}/{name}',
        'content': '/contents/{path}?ref={branch}',
        'branch': '/branches/{branch}'
    },
    'bitbucket.org': {
        'repo': 'https://api.bitbucket.com/2.0/repositories/{owner}/{name}',
        # 'content': '/src/{branch}/{path}',  # ?format=meta
        'content': '/src/{branch}/{path}?format=meta',
        'branch': '/commit/{branch}'
    }
}
REPO_CHECK_KEYS = ('provider', 'owner', 'name', 'path', 'branch', 'hash', 'access')


class GitManage:
    def __init__(self, *args, **kwargs):
        self.__repo_obj = None  # { provider owner name path branch hash update access }
        self.new_hash = None  # if yes - need to update
        self.error = None

    @property
    def need_update(self):
        # len(<hash>) == 40
        if self.__repo_obj:
            return self.new_hash == self.__repo_obj['hash']
        return False

    @property
    def repo(self):
        return self.__repo_obj

    @repo.setter
    def repo(self, value):
        """ Init repo_obj and check it by hash """
        # check_keys = ('provider', 'owner', 'name', 'path', 'branch', 'hash', 'access')
        if isinstance(value, dict) and all(k in REPO_CHECK_KEYS for k in value):
            self.__repo_obj = value
        else:
            self.error = 'Not a valid repo object'
            self.__repo_obj = None

    def check_url(self, link):
        """ Create repo_obj from URL """
        # FIXME: folder names with special chars
        url_items = re.match(r'^http[s]?\:\/\/([^\/]+)\/(\w+)\/(\w+)(?:\/(?:tree|src)\/(\w+)\/?)?(.+)?', link)
        if url_items:
            self.repo = {
                'provider': url_items.group(1), 'owner': url_items.group(2), 'name': url_items.group(3),
                'branch': url_items.group(4) if url_items.group(4) else 'master',
                'path': self.__path_fix(url_items.group(5)) if url_items.group(5) else '',
                'hash': None, 'access': ('meoook', 'j3262new')
            }
            return self.check_repo()
        else:
            self.error = f'Repo URL parse error: {link}'
            return False

    def __api_url_create(self, in_path=None, as_branch=False):
        """ Builder for API URLs by provider """
        provider_obj = KNOWN_PROVIDERS[self.__repo_obj['provider']]
        owner = self.__repo_obj['owner']
        name = self.__repo_obj['name']
        branch = self.__repo_obj['branch']
        path = in_path if in_path else ''
        url_format = provider_obj['repo'] + (provider_obj['branch'] if as_branch else provider_obj['content'])
        return url_format.format(owner=owner, name=name, branch=branch, path=path)

    def check_repo(self):
        """ Check access and exist status. """
        provider = self.__repo_obj['provider']
        if self.error or not self.__repo_obj:
            return False
        if self.__repo_obj['provider'] not in KNOWN_PROVIDERS:
            self.error = f'Git provider {provider} not configured'
            return False
        link = self.__api_url_create(self.__repo_obj['path'])
        # Check connect
        resp = self.__request_url(link)
        if not resp:
            return False
        if provider == 'github.com':
            return self.__check_github(resp)
        elif provider == 'bitbucket.org':
            return self.__check_bitbucket(resp)
        else:
            self.error = f'Method repo_obj_check not set for provider: {provider}'
            return False

    def __check_bitbucket(self, resp):
        """ Check response and get hash """
        if 'commit' in resp and 'type' in resp and resp['type'] == 'commit_directory':
            self.new_hash = resp['commit']['hash']
            return True
        self.error = 'Bitbucket api error. Wrong response.'
        return False

    def __check_github(self, resp):     # TODO: can get data as symlink with no context
        """ Check response and get hash """
        if not isinstance(resp, list):
            self.error = 'Github api error. Wrong response.'
            return False
        # Get hash from content of head folder. If head folder is root folder -> find hash in branch.
        if self.__repo_obj['path']:
            updated_path, search_item = self.__path_cut(self.__repo_obj['path'])
            link = self.__api_url_create(updated_path)
            resp = self.__request_url(link)
            if not resp:
                return False
            obj = self.__find_by_name(search_item, resp)
            if obj and 'path' in obj and 'sha' in obj and 'size' in obj:
                self.new_hash = obj['sha']
                return True
        else:
            link = self.__api_url_create(as_branch=True)
            resp = self.__request_url(link)
            if not resp:
                return False
            if 'commit' in resp and 'name' in resp and resp['name'] == self.__repo_obj['branch']:
                self.new_hash = resp['commit']['sha']
                return True
        self.error = f'Wrong response for URL: {link}'
        return False

    def __request_url(self, link):
        """ Check url and return JSON """
        headers = {'Content-type': 'application/vnd.github.VERSION.html'}
        resp = requests.get(link, headers=headers) if self.__repo_obj['access'] else requests.get(link, headers=headers)
        if resp.status_code == requests.codes.ok:
            return resp.json()
        self.error = f'Connect error: {link}'
        return None

    def update_files(self, file_list):
        """ Return list of success downloaded files """
        uploaded_files = []
        if self.error:
            pass
        elif not self.__repo_obj:
            self.error = 'Repo object not set'
        elif not isinstance(file_list, list):
            self.error = 'Params error - need list of file obj'
        else:
            checked_files = self.__check_files(file_list)
            uploaded_files = self.__download_file_list(checked_files)
        return uploaded_files

    def __check_files(self, file_list):
        """ Check files_obj (name, hash) on exist and need to update. """
        return_arr = []
        for file_item in file_list:
            item_to_add = {**file_item, 'success': False, 'download_url': None}
            link = self.__api_url_create(in_path=f'{self.__repo_obj["path"]}/{file_item["name"]}')
            resp = self.__request_url(link)
            if not resp:
                continue
            if self.__repo_obj['provider'] == 'github.com':
                if 'sha' in resp and 'download_url' in resp and 'name' in resp and resp['name'] == file_item['name']:
                    item_to_add['success'] = True
                    if resp['sha'] != file_item['hash']:
                        item_to_add['hash'] = resp['sha']
                        item_to_add['download_url'] = resp['download_url']
            elif self.__repo_obj['provider'] == 'bitbucket.org':
                if 'links' in resp and 'commit' in resp and 'type' in resp and resp['type'] == 'commit_file':
                    item_to_add['success'] = True
                    if resp['commit']['hash'] != file_item['hash']:
                        item_to_add['hash'] = resp['commit']['hash']
                        item_to_add['download_url'] = resp['links']['self']['href']
            return_arr.append(item_to_add)
        return return_arr

    def __download_file_list(self, file_list):
        """ Download file list and return seccuss file list () """
        success_upload_list = []
        for file_item in file_list:
            if file_item['success'] and file_item['download_url']:
                try:
                    self.__download_file(file_item['download_url'], file_item['path'])
                except requests.exceptions.ConnectionError:
                    # LOGGER
                    continue
                else:
                    success_upload_list.append(file_item)
        return success_upload_list

    @staticmethod
    def __download_file(download_url, file_path):
        """ Download file from repo. Then update or create file """
        # NOTE the stream=True parameter below
        with requests.get(download_url, stream=True) as r:
            if r.status_code == requests.codes.ok:
                # r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)

    @staticmethod
    def __path_fix(full_path):
        """ Remove filename from path if it's found """
        path_items = re.match(r'^(.+)\/(?:[^\/\s]+\.[^\/\s]+)?$', full_path)
        return path_items.group(1) if path_items else full_path

    @staticmethod
    def __path_cut(folder_path):
        """ Remove last folder name from path """
        cut_path = re.match(r'^(?:(.*)\/)?(\w+)\/?$', folder_path)
        return (cut_path.group(1), cut_path.group(2)) if cut_path else ('', '')

    @staticmethod
    def __find_by_name(name, arr):
        for item in arr:
            if 'name' in item and item['name'] == name:
                return item
        else:
            return None
