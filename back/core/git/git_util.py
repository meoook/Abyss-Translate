import os
import requests


class GitProviderUtils:
    """ Util class to work with git repositories (morph class for git_providers) """

    _commit_msg = 'Create/update translated copy {path} from localize'

    def __init__(self, git_obj, abyss_access, root, repo, file, upload=None):
        self.__access = None
        self._git = git_obj
        self.__abyss_access = abyss_access
        self.__url_root = root
        self.__url_suffix_repo = repo
        self.__url_suffix_file = file if file else repo
        self.__url_suffix_upload = upload if upload else file

    @property
    def repo_http_url(self):
        return self._url_http_format.format(**self._git)

    @property
    def _access(self):
        """ Auth header for selected repo or use abyss access """
        if self.__access or self.__access_get():
            return self.__access

    def __access_get(self):
        if self._git['access']:
            if self._git['access']['type'] == 'basic':
                return {'Authorization': f'Basic {self._git["access"]["token"]}'}
            elif self._git['access']['type'] == 'token':
                return {'Authorization': f'Token {self._git["access"]["token"]}'}
            elif self._git['access']['type'] == 'beaver':
                return {'Authorization': f'Beaver {self._git["access"]["token"]}'}
            elif self._git['access']['type'] == 'oauth':
                pass  # Get Auth token
        else:
            self.__access = self.__abyss_access
        return True

    @property
    def _url_http_format(self):
        """ Return format to create http URLs (for browser) """
        return self.__url_root + self.__url_suffix_repo

    @property
    def _url_folder_format(self):
        """ Return format to create folders or projects request URLs """
        return self.__url_root + self.__url_suffix_repo

    @property
    def _url_file_format(self):
        """ Return format to create file requests URLs """
        return self.__url_root + self.__url_suffix_file

    @property
    def _url_upload_format(self):
        """ Return format to create file upload request URLs """
        return self.__url_root + self.__url_suffix_upload

    @staticmethod
    def _request(request_obj):
        """ Handle connection errors """
        err = f'Connect {request_obj["url"]} error: '
        try:
            with requests.request(**request_obj) as resp:
                code = resp.status_code
        except requests.exceptions.ConnectionError:
            return None, err + 'network error'
        if code < 300:
            return resp, None
        elif code == 403:
            return None, err + 'no access'
        elif code == 404:
            return None, err + 'not found'
        else:
            return None, err + f'unknown code: {code}'

    def _pre_download_file(self, link, path, old_sha, new_sha, err, add_header=None):
        """ Check errors and download if checked """
        if err:
            return None, err
        if old_sha == new_sha:
            return None, None   # File hash not updated
        head = {**self._access, **add_header} if add_header else self._access
        success, err = self._download_file(path, link, head)
        return (None, err) if err else (new_sha, None)

    @staticmethod
    def _download_file(path, link, head):
        """ Download and save file on disk """
        try:
            filo = open(path, 'wb')
        except IOError:
            return None, f'IO error {path}'

        try:
            download_obj = {'url': link, 'headers': head}
            response = requests.get(**download_obj, stream=True)
        except requests.exceptions.ConnectionError:
            return None, f'network error {link}'
        if response.status_code != requests.codes.ok:
            return None, f'response error - code: {response.status_code}'
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=8192):
            try:
                filo.write(chunk)
            except IOError:
                return None, f'IO error {path}'
        filo.close()
        response.close()
        return True, None

    @staticmethod
    def _read_file_data(path):
        try:
            with open(path, 'rb') as filo:
                data = filo.read()
        except FileNotFoundError:
            return None, f'File "{path}" not found'
        except IOError:
            return None, f'IO Error read file {path}'
        return data, None

    def _file_download_request_url(self, path):
        """ URL with filename to download file """
        filename = os.path.basename(path)
        return self._url_file_format.format(**self._obj_with_filename(filename))

    def _file_upload_request_values(self, path, access):
        """ Util function to create some request data """
        filename = os.path.basename(path)
        git_path = f'{self._git["path"]}/{filename}' if self._git["path"] else filename
        link = self._url_upload_format.format(**self._obj_with_filename(filename))
        head = {**access, 'Content-type': 'application/json', 'Accept': 'application/json'}
        return git_path, link, head

    def _file_upload_sha(self, req_obj, lambda_fn):
        response, err = self._request(req_obj)
        if err:
            return None, err
        try:
            resp = response.json()
        except ValueError:
            return None, f'Response json parse error {req_obj["url"]}'
        return lambda_fn(resp), None

    def _obj_with_filename(self, filename):
        """ Add filename to object path """
        return {**self._git, 'path': self._path_with_filename(self._git["path"], filename)}

    @staticmethod
    def _path_with_filename(path, filename):
        return f'{path}/{filename}' if path else filename
