import os
import requests


class GitProviderUtils:
    """ Util class to work with git repositories (morph class for git_providers) """

    _commit_msg = 'Create/update translated copy {file_path} from localize'

    def __init__(self, git_obj: dict, abyss_access: dict, root: str, repo: str, file: str = None, upload: str = None):
        self.__access = None
        self._git = git_obj
        self.__abyss_access = abyss_access
        self.__url_root = root
        self.__url_suffix_repo = repo
        self.__url_suffix_file = file if file else repo
        self.__url_suffix_upload = upload if upload else file

    def repo_get_sha(self):
        """ Get repository new hash with err status """
        raise NotImplemented('Method repo_get_sha not implemented in root(Git*Connect) class')

    def file_update(self, path: str, old_sha: str):
        """ Check file hash and download if updated """
        raise NotImplemented('Method file_update not implemented in root(Git*Connect) class')

    def file_upload(self, path: str, old_sha: str):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        raise NotImplemented('Method file_upload not implemented in root(Git*Connect) class')

    @property
    def repo_http_url(self):
        """ Repository object http url (not used) """
        return self._url_http_format.format(**self._git)

    @property
    def _access(self):  # TODO: Remake
        """ Auth data (token or header) for selected repo or used abyss access as default """
        if self.__access or self.__access_get():
            return self.__access

    def __access_get(self):  # TODO: Remake
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

    def _url_download_file(self, file_path: str):
        """ URL with filename to download file """
        filename = os.path.basename(file_path)
        return self._url_file_format.format(**self._obj_with_filename(filename))

    @property
    def _url_http_format(self):
        """ Format to create http URLs (for browser) """
        return self.__url_root + self.__url_suffix_repo

    @property
    def _url_folder_format(self):
        """ Format to create folders or projects request URLs """
        return self.__url_root + self.__url_suffix_repo

    @property
    def _url_file_format(self):
        """ Format to create file requests URLs """
        return self.__url_root + self.__url_suffix_file

    @property
    def _url_upload_format(self):
        """ Format to create file upload request URLs """
        return self.__url_root + self.__url_suffix_upload

    @staticmethod
    def _request(request_object):
        """ Handle connection errors """
        """ Handle connection errors """
        err = f'Connect {request_object["url"]} error: '
        try:
            print('REQUEST IS', request_object)
            with requests.request(**request_object) as response:
                code = response.status_code
                if code < 300:
                    if not response.text:
                        return response, None
                    try:
                        return response.json(), None
                    except ValueError:
                        return None, f'json parse error'
                elif code == 400:
                    return None, err + 'request params error'
                elif code == 403:
                    return None, err + 'no access'
                elif code == 404:
                    return None, err + 'not found'
                else:
                    return None, err + f'unknown code {code}'
        except requests.exceptions.ConnectionError:
            return None, err + 'network error'

    def _file_upload_request_values(self, path, access):
        """ Util function to create some request data """
        filename = os.path.basename(path)
        git_path = f'{self._git["path"]}/{filename}' if self._git["path"] else filename
        link = self._url_upload_format.format(**self._obj_with_filename(filename))
        head = {**access, 'Content-type': 'application/json', 'Accept': 'application/json'}
        return git_path, link, head

    def _file_upload_get_sha(self, req_obj, lambda_fn):
        response, err = self._request(req_obj)
        if err:
            return None, err
        return lambda_fn(response), None

    def _file_pre_download(self, link, path, old_sha, new_sha, err, add_header=None):
        """ Check errors and download if checked """
        if err:
            return None, err
        if old_sha == new_sha:
            return None, None  # File hash not updated
        head = {**self._access, **add_header} if add_header else self._access
        success, err = self._file_download(path, link, head)
        return (None, err) if err else (new_sha, None)

    @staticmethod
    def _file_download(path: str, link: str, head: str):
        """ Download and save file on disk """
        try:
            with open(path, 'wb') as filo:
                download_obj = {'url': link, 'headers': head}
                with requests.get(**download_obj, stream=True) as response:
                    response.raise_for_status()
                    if response.status_code != requests.codes.ok:
                        return None, f'response error - code: {response.status_code}'
                    for chunk in response.iter_content(chunk_size=8192):
                        filo.write(chunk)
                    return True, None
        except FileNotFoundError:
            return None, f'Not found err: {path}'
        except IOError:
            return None, f'IO error {path}'
        except requests.exceptions.ConnectionError:
            return None, f'network error {link}'

    @staticmethod
    def _file_read_data(path: str):
        """ Safe read file data """
        try:
            with open(path, 'rb') as filo:
                data = filo.read()
        except FileNotFoundError:
            return None, f'File "{path}" not found'
        except IOError:
            return None, f'IO Error read file {path}'
        return data, None

    @staticmethod
    def _path_with_filename(path: str, filename: str):
        """ Fixed path if no root folder - can be reimplement to url encode in "extend" classes """
        return f'{path}/{filename}' if path else filename

    def _obj_with_filename(self, filename: str):
        """ Return object with added filename in it path attribute """
        return {**self._git, 'path': self._path_with_filename(self._git["path"], filename)}
