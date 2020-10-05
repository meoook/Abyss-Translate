import os
import requests

from core.git.git_oauth2 import GitOAuth2


class GitProviderUtils:
    """ Util class to work with git repositories (morph class for git_providers) """

    _commit_msg = 'Create/update translated copy {file_path} from localize'

    def __init__(self, git_obj, abyss_access, root, repo, file=None, upload=None):
        self.__token = None
        self.__auth_header = None
        self._git = git_obj
        self.__abyss_access = abyss_access
        self.__url_root = root
        self.__url_suffix_repo = repo
        self.__url_suffix_file = file if file else repo
        self.__url_suffix_upload = upload if upload else file

    def repo_get_sha(self):
        """ Get repository new hash with err status """
        raise NotImplementedError('Method repo_get_sha not implemented in root(Git*Connect) class')

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        raise NotImplementedError('Method file_update not implemented in root(Git*Connect) class')

    def file_upload(self, path, old_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        raise NotImplementedError('Method file_upload not implemented in root(Git*Connect) class')

    @property
    def repo_http_url(self):
        """ Repository object http url (not used) """
        return self._url_http_format.format(**self._git)

    @property
    def _auth_header(self):
        """ Authorization header for selected repo or abyss access by default """
        if not self.__auth_header:
            self.__auth_set()
        return self.__auth_header

    def __auth_set(self):
        access_type = None
        access_token = None
        if self._git['access']:
            access_type = self._git['access']['type']
            access_token = self.__token_get_from_type(access_type, self._git["access"]["token"])
        if not access_token:  # If fail - Get abyss access token
            access_type = self.__abyss_access['type']
            access_token = self.__token_get_from_type(access_type, self.__abyss_access['token'])
        assert access_token, "Auth get failed"
        self.__token = access_token
        self.__auth_header = self.__auth_header_get(access_type, access_token)

    def __auth_header_get(self, access_type, access_token):
        """ Return auth header by type """
        if access_type == 'basic':
            return {'Authorization': f'Basic {access_token}'}
        elif access_type == 'token':
            return self._auth_header_get_by_token(access_token)
        elif access_type == 'bearer':
            return {'Authorization': f'Bearer {access_token}'}
        elif access_type == 'oauth':
            return self._auth_header_get_by_oauth(access_token)
        else:
            return {}

    @staticmethod
    def _auth_header_get_by_token(access_token):
        """ Return auth header by token (can be changed by provider) """
        return {'Authorization': f'Token {access_token}'}

    @staticmethod
    def _auth_header_get_by_oauth(access_token):
        """ Return auth header by oauth (can be changed by provider) """
        return {'Authorization': f'Bearer {access_token}'}

    @property
    def _token(self):
        if not self.__token:
            self.__auth_set()
        return self.__token

    def __token_get_from_type(self, token_type, token_value):
        if token_type in ['basic', 'token', 'bearer']:
            return token_value
        elif token_type == 'oauth':
            oauth = GitOAuth2(self._git['provider'])
            token, err = oauth.access_token(token_value)
            if not err:
                return token
        return None

    def _url_download_file(self, file_path):
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
        err = f'Connect {request_object["url"]} error: '
        try:
            with requests.request(**request_object) as response:
                code = response.status_code
                if code < 300:
                    if not response.text:
                        return response, None  # Data in headers
                    try:
                        return response.json(), None
                    except ValueError:
                        return None, 'json parse error'
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
        head = {**self._auth_header, **add_header} if add_header else self._auth_header
        success, err = self._file_download(path, link, head)
        return (None, err) if err else (new_sha, None)

    @staticmethod
    def _file_download(path, link, head):
        """ Download and save file on disk """
        try:
            with open(path, 'wb') as filo:
                download_obj = {'url': link, 'headers': head}
                print('DOWNLOAD OBJ', download_obj)
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
    def _file_read_data(path):
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
    def _path_with_filename(path, filename):
        """ Fixed path if no root folder - can be reimplement to url encode in "extend" classes """
        return f'{path}/{filename}' if path else filename

    def _obj_with_filename(self, filename):
        """ Return object with added filename in it path attribute """
        return {**self._git, 'path': self._path_with_filename(self._git["path"], filename)}
