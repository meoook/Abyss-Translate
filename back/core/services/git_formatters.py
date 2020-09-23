import json
from urllib import parse
import base64


class GitFormatter:
    """ Basic class structure for git parser """

    _commit_msg = 'Create/update translated copy {path} from localize'

    def __init__(self, root, repo, file=None, upload=None, h_request=None, h_upload=None):
        self.__url_root = root
        self.__url_suffix_repo = repo
        self.__url_suffix_file = file if file else repo
        self.__url_suffix_upload = upload if upload else file
        self.__header_request = h_request if h_request else {}
        self.__header_upload = h_upload if h_upload else {}

    @property
    def headers(self):
        return {**self.__header_request, 'Content-type': 'application/json'}

    def url_create(self, git_obj, filename=''):
        """ Create URL from format """
        if filename:
            return self._url_file_format.format(**self._obj_with_filename(git_obj, filename))
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
        except json.decoder.JSONDecodeError:
            return f'Error JSON decode response: {response.text.decode()}'

    @staticmethod
    def hash_from_resp_upload(response):
        """ Get file translated copy hash after uploaded to git repository """
        try:
            response = response.json()
            return response['content']['sha']
        except (KeyError, TypeError):
            pass
        return False

    def request_obj_for_file_upload(self, git_obj, git_access, git_file_name, git_file_hash, data):
        """ Create full request object with method, url, headers, and data """
        path, link, head = self._create_request_util_values(git_obj, git_file_name, git_access)
        data_coded = base64.b64encode(data).decode('utf-8')
        obj = {
            'message': self._commit_msg.format(path=path),
            'content': data_coded,
            'branch': git_obj['branch'],
            'sha': git_file_hash,
        }
        return {'method': 'PUT', 'url': link, 'headers': head, 'data': json.dumps(obj)}

    def _create_request_util_values(self, obj, filename, access):
        """ Util function to create some request data """
        path = self._path_with_filename(obj["path"], filename)
        link = self._url_upload_format.format(**self._obj_with_filename(obj, filename))
        head = {**self.__header_upload, **access, 'Content-type': 'application/json'}
        return path, link, head

    def _obj_with_filename(self, obj, filename):
        """ Add filename to object path """
        return {**obj, 'path': self._path_with_filename(obj["path"], filename)}

    @staticmethod
    def _path_with_filename(path, filename):
        return f'{path}/{filename}' if path else filename

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


class GitHubFormatter(GitFormatter):
    def __init__(self):
        root = 'https://api.github.com/repos/{owner}/{name}'
        repo = '/contents/{path}?ref={branch}'
        file = '/contents/{path}?ref={branch}'
        header_request = {'Accept': 'application/vnd.github.VERSION.object', }
        header_upload = {'Accept': 'application/vnd.github.v3+json'}
        super().__init__(root, repo, file, None, header_request, header_upload)

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['sha'], base64.b64decode(response['content'])
            return response['sha'], None
        except (KeyError, TypeError):
            pass
        return None, 'Error parsing response with code 200'

    @staticmethod
    def hash_from_resp_upload(response):
        try:
            response = response.json()
            return response['content']['sha']
        except (KeyError, TypeError):
            pass
        return False

    def request_obj_for_file_upload(self, git_obj, git_access, git_file_name, git_file_hash, data):
        path, link, head = self._create_request_util_values(git_obj, git_file_name, git_access)
        data_coded = base64.b64encode(data).decode('utf-8')
        obj = {
            'message': self._commit_msg.format(path=path),
            'content': data_coded,
            'branch': git_obj['branch'],
            'sha': git_file_hash,
        }
        return {'method': 'PUT', 'url': link, 'headers': head, 'data': json.dumps(obj)}


class BitBucketFormatter(GitFormatter):
    def __init__(self):
        root = 'https://api.bitbucket.com/2.0/repositories/{owner}/{name}'
        repo = '/src/{branch}/{path}?format=meta'  # '/commit/{branch}'
        file = '/src/{branch}/{path}?format=meta'
        upload = '/src'
        # header_request = {"Content-Type": "application/x-www-form-urlencoded"}
        header_upload = {"Content-Type": "application/x-www-form-urlencoded"}
        super().__init__(root, repo, file, upload, None, header_upload)

    # @property
    # def headers(self):
    #     # return {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    #     return {}

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['commit']['hash'], response['links']['self']['href']
            return response['commit']['hash'], None
        except (KeyError, TypeError):
            pass
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

    @staticmethod
    def hash_from_resp_upload(response):
        try:
            response = response.json()
            return response['content']['sha']
        except (KeyError, TypeError):
            pass
        return False

    def request_obj_for_file_upload(self, git_obj, git_access, git_file_name, git_file_hash, data):
        path, link, _ = self._create_request_util_values(git_obj, git_file_name, git_access)
        head = {**git_access, "Content-Type": "application/x-www-form-urlencoded"}
        path = '/' + path
        datap = data.decode('utf-8')
        params = [
            (path, datap),
            ('message', self._commit_msg.format(path=path)),
            ('branch', git_obj['branch']),
            ('author', 'meokok <meoook@gmail.com>'),
            ('files', path)
            # 'access_token': 'r7zVQH58rWfMX9oVWydrA4A8',
        ]
        obj = {
            path: data.decode('utf-8'),
            'message': self._commit_msg.format(path=path),
            'branch': git_obj['branch'],
            'author': 'meokok <meoook@gmail.com>',
            'files': path,
            # 'access_token': 'r7zVQH58rWfMX9oVWydrA4A8',
        }
        files = {
            path: datap
        }
        # return {'method': 'POST', 'url': link, 'headers': head, 'data': json.dumps(obj)}
        # return {'method': 'POST', 'url': link, 'headers': head, 'data': obj}
        # return {'method': 'POST', 'url': link, 'headers': head, 'files': {'name': ('filename', fileobj)}}
        # return {'method': 'POST', 'url': link, 'headers': head, 'params': json.dumps(obj)}
        return {'method': 'POST', 'url': link, 'headers': head, 'files': files}


class GitLabFormatter(GitFormatter):
    def __init__(self):
        root = 'https://gitlab.com/api/v4/projects/{owner_name}/repository/'
        repo = 'commits?ref_name={branch}&path={path}'
        file = 'files/{path}?ref={branch}'
        super().__init__(root, repo, file)

    def url_create(self, git_obj, filename=''):
        """ Create URL from format """
        obj = {**git_obj, 'owner_name': parse.quote_plus(f'{git_obj["owner"]}/{git_obj["name"]}')}
        if filename:
            path = self._path_with_filename(obj["path"], filename)
            obj["path"] = parse.quote_plus(path)
            return self._url_file_format.format(**obj)
        obj['path'] = parse.quote_plus(obj['path'])
        return self._url_folder_format.format(**obj)

    @staticmethod
    def data_from_resp(response, as_file=False):
        try:
            response = response.json()
            if as_file:
                return response['blob_id'], base64.b64decode(response['content'])
            return response[0]['id'], None
        except (KeyError, TypeError):
            return None, 'Error parsing response with code 200'

    @staticmethod
    def hash_from_resp_upload(response):
        try:
            response = response.json()
            return response['file_path']
        except (KeyError, TypeError):
            pass
        return False

    def request_obj_for_file_upload(self, git_obj, git_access, git_file_name, git_file_hash, data):
        obj_formatted = {**git_obj, 'owner_name': parse.quote_plus(f'{git_obj["owner"]}/{git_obj["name"]}')}
        path, link, head = self._create_request_util_values(obj_formatted, git_file_name, git_access)
        data_coded = base64.b64encode(data).decode('utf-8')
        obj = {
            'commit_message': self._commit_msg.format(path=f'{git_obj["path"]}/{git_file_name}'),
            'content': data_coded,
            'branch': git_obj['branch'],
            'encoding': 'base64',
        }
        method = 'PUT' if git_file_hash else 'POST'
        return {'method': method, 'url': link, 'headers': head, 'data': json.dumps(obj)}

    @staticmethod
    def _path_with_filename(path, filename):
        result_path = f'{path}/{filename}' if path else filename
        return parse.quote_plus(result_path)
