import base64
import json
from urllib import parse

from core.services.git_interface.git_auth import AuthGitHub, AuthGitLab, AuthBitBucket
from core.services.git_interface.git_util import GitProviderUtils


class GitHubConnect(GitProviderUtils):

    def __init__(self, git_obj):
        root = 'https://api.github.com/repos/{owner}/{name}'
        repo = '/contents/{path}?ref={branch}'
        file = '/contents/{path}?ref={branch}'
        auth = AuthGitHub()
        super().__init__(auth, git_obj, root, repo, file)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._url_download_file(path)
        new_sha, err = self.__sha_get(link)
        header = {**self._auth_header, 'Accept': 'application/vnd.github.v3.raw'}
        return self._file_pre_download(link, path, old_sha, new_sha, err, header)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._file_read_data(path)
        if err:
            return None, err
        data_coded = base64.b64encode(data_binary).decode('utf-8')
        git_path, link, head = self._file_upload_request_values(path, self._auth_header)
        obj = {
            'message': self._commit_msg.format(file_path=git_path),
            'content': data_coded,
            'branch': self._git['branch'],
            'sha': git_file_sha,
        }
        req_obj = {'method': 'PUT', 'url': link, 'headers': head, 'data': json.dumps(obj)}

        def fn(x):  # Lambda function to find sha
            return x['content']['sha']

        return self._file_upload_get_sha(req_obj, fn)

    def __sha_get(self, link):
        req_obj = {'method': 'HEAD', 'url': link, 'headers': self._auth_header}
        response, err = self.make_request(req_obj)
        return (None, err) if err else self.__sha_from_header(response.headers)

    @staticmethod
    def __sha_from_header(headers):
        sha_header = headers.get('ETag')
        if not sha_header:
            return None, 'sha not found in header'
        sha_header = sha_header.split('"')[1]
        return (sha_header, None) if len(sha_header) == 40 else (None, 'error sha check')

    @staticmethod
    def _auth_header_get_by_oauth(access_token):
        """ Return auth header by oauth (can be changed by provider) """
        return {'Authorization': f'token {access_token}'}


class GitLabConnect(GitProviderUtils):

    def __init__(self, git_obj):
        git_obj = {**git_obj, 'owner_name': self._path_with_filename(git_obj['owner'], git_obj['name'])}
        root = 'https://gitlab.com/api/v4/projects/{owner_name}/repository/'
        repo = 'commits?ref={branch}&path={path}'
        file = 'files/{path}/raw?ref={branch}'
        upload = 'files/{path}?ref={branch}'
        auth = AuthGitLab()
        super().__init__(auth, git_obj, root, repo, file, upload)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._url_download_file(path)
        new_sha, err = self.__sha_get(link, True)
        return self._file_pre_download(link, path, old_sha, new_sha, err, self._auth_header)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._file_read_data(path)
        if err:
            return None, err
        data_coded = base64.b64encode(data_binary).decode('utf-8')
        git_path, link, head = self._file_upload_request_values(path, self._auth_header)
        obj = {
            'commit_message': self._commit_msg.format(file_path=git_path),
            'content': data_coded,
            'branch': self._git['branch'],
            'encoding': 'base64',
        }
        method = 'PUT' if git_file_sha else 'POST'
        req_obj = {'method': method, 'url': link, 'headers': head, 'data': json.dumps(obj)}

        def fn(x):  # Lambda function to find sha
            return x['file_path']

        return self._file_upload_get_sha(req_obj, fn)

    def __sha_get(self, link, as_file=False):
        method = 'HEAD' if as_file else 'GET'
        req_obj = {'method': method, 'url': link, 'headers': self._auth_header}
        response, err = self.make_request(req_obj)
        return (None, err) if err else self.__sha_from_response(response, as_file)

    def __sha_from_response(self, response, as_file):
        if as_file:
            return self.__sha_from_header(response.headers)
        try:
            return response[0]['id'], None
        except (KeyError, TypeError):
            return None, 'Comment id not found in response'

    @staticmethod
    def __sha_from_header(headers):
        sha_header = headers.get('X-Gitlab-Blob-Id')
        if not sha_header:
            return None, 'sha not found in header'
        return (sha_header, None) if len(sha_header) == 40 else (None, 'error sha check')

    @staticmethod
    def _path_with_filename(path, filename):
        result_path = f'{path}/{filename}' if path else filename
        return parse.quote_plus(result_path)

    @staticmethod
    def _auth_header_get_by_token(access_token):
        return {'PRIVATE-TOKEN': access_token}


class BitBucketConnect(GitProviderUtils):

    def __init__(self, git_obj):
        root = 'https://api.bitbucket.com/2.0/repositories/{owner}/{name}'
        repo = '/src/{branch}/{path}'
        file = '/src/{branch}/{path}'
        upload = '/src/'
        auth = AuthBitBucket()
        super().__init__(auth, git_obj, root, repo, file, upload)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._url_download_file(path) + '?access_token=' + self._auth_token
        new_sha, err = self.__sha_get(link)
        # header = self._auth_header
        return self._file_pre_download(link, path, old_sha, new_sha, err)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._file_read_data(path)
        if err:
            return None, err
        # data_coded = base64.b64encode(data_binary).decode('utf-8')
        data_coded = data_binary.decode('utf-8')
        git_path, link, _ = self._file_upload_request_values(path, self._auth_header)
        head = {'Content-Type': 'application/x-www-form-urlencoded'}
        # application/x-www-form-urlencoded
        # ?token={token}
        # obj = {
        #     'message': self._commit_msg.format(file_path=git_path),
        #     'content': data_coded,
        #     'branch': self._git['branch'],
        #     'sha': git_file_sha,
        # }
        obj = {
            'message': self._commit_msg.format(file_path=git_path),
            f'/{git_path}': data_coded,
            'branch': self._git['branch'],
            'token': self._auth_token,
        }
        # req_obj = {'method': 'POST', 'url': link, 'headers': head, 'data': json.dumps(obj)}
        req_obj = {'method': 'POST', 'url': link, 'headers': head, 'data': obj}

        def fn(x):  # Lambda function to find sha
            return x['commit']['hash']

        return self._file_upload_get_sha(req_obj, fn)

    def __sha_get(self, link):
        params = {'format': 'meta', 'access_token': self._auth_token}
        req_obj = {'method': 'GET', 'url': link, 'params': params}
        response, err = self.make_request(req_obj)
        return (None, err) if err else self.__sha_from_response(response)

    @staticmethod
    def __sha_from_response(response):
        try:
            return response['commit']['hash'], None
        except (KeyError, TypeError):
            return None, 'Commit not found in response'
