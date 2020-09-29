import base64
import json
from urllib import parse

from core.git.git_util import GitProviderUtils


class GitHubConnect(GitProviderUtils):

    def __init__(self, git_obj):
        root = 'https://api.github.com/repos/{owner}/{name}'
        repo = '/contents/{path}?ref={branch}'
        file = '/contents/{path}?ref={branch}'
        abyss_access = {'Authorization': 'Basic bWVvb29rOmozMjYybmV3'}  # FIXME: It's my credentials omg
        super().__init__(git_obj, abyss_access, root, repo, file)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._file_download_request_url(path)
        new_sha, err = self.__sha_get(link)
        add_header = {'Accept': 'application/vnd.github.v3.raw'}
        return self._pre_download_file(link, path, old_sha, new_sha, err, add_header)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._read_file_data(path)
        if err:
            return None, err
        data_coded = base64.b64encode(data_binary).decode('utf-8')
        git_path, link, head = self._file_upload_request_values(path, self._access)
        obj = {
            'message': self._commit_msg.format(path=git_path),
            'content': data_coded,
            'branch': self._git['branch'],
            'sha': git_file_sha,
        }
        req_obj = {'method': 'PUT', 'url': link, 'headers': head, 'data': json.dumps(obj)}

        def fn(x):  # Lambda function to find sha
            return x['content']['sha']
        return self._file_upload_sha(req_obj, fn)

    def __sha_get(self, link):
        req_obj = {'method': 'HEAD', 'url': link, 'headers': self._access}
        response, err = self._request(req_obj)
        return (None, err) if err else self.__sha_from_header(response.headers)

    @staticmethod
    def __sha_from_header(headers):
        sha_header = headers.get('ETag')
        if not sha_header:
            return None, 'sha not found in header'
        sha_header = sha_header.split('"')[1]
        return (sha_header, None) if len(sha_header) == 40 else (None, 'error sha check')


class GitLabConnect(GitProviderUtils):

    def __init__(self, git_obj):
        git_obj = {**git_obj, 'owner_name': self._path_with_filename(git_obj['owner'], git_obj['name'])}
        root = 'https://gitlab.com/api/v4/projects/{owner_name}/repository/'
        repo = 'commits?ref={branch}&path={path}'
        file = 'files/{path}/raw?ref={branch}'
        upload = 'files/{path}?ref={branch}'
        abyss_access = {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'}  # FIXME: It's my credentials omg
        super().__init__(git_obj, abyss_access, root, repo, file, upload)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._file_download_request_url(path)
        new_sha, err = self.__sha_get(link, True)
        return self._pre_download_file(link, path, old_sha, new_sha, err)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._read_file_data(path)
        if err:
            return None, err
        data_coded = base64.b64encode(data_binary).decode('utf-8')
        git_path, link, head = self._file_upload_request_values(path, self._access)
        obj = {
            'commit_message': self._commit_msg.format(path=git_path),
            'content': data_coded,
            'branch': self._git['branch'],
            'encoding': 'base64',
        }
        method = 'PUT' if git_file_sha else 'POST'
        req_obj = {'method': method, 'url': link, 'headers': head, 'data': json.dumps(obj)}

        def fn(x):  # Lambda function to find sha
            return x['file_path']
        return self._file_upload_sha(req_obj, fn)

    def __sha_get(self, link, as_file=False):
        method = 'HEAD' if as_file else 'GET'
        req_obj = {'method': method, 'url': link, 'headers': self._access}
        response, err = self._request(req_obj)
        return (None, err) if err else self.__sha_from_response(response, as_file)

    def __sha_from_response(self, response, as_file):
        if as_file:
            return self.__sha_from_header(response.headers)
        try:
            response = response.json()
            return response[0]['id'], None
        except (KeyError, TypeError):
            return None, 'Comment id not found in response'
        except ValueError:
            return None, 'Json parse error'

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


class BitBucketConnect(GitProviderUtils):

    def __init__(self, git_obj):
        root = 'https://api.bitbucket.com/2.0/repositories/{owner}/{name}'
        repo = '/src/{branch}/{path}?format=meta'  # '/commit/{branch}'
        file = '/src/{branch}/{path}'
        upload = '/src'
        abyss_access = {}  # FIXME: No credentials
        super().__init__(git_obj, abyss_access, root, repo, file, upload)

    def repo_get_sha(self):
        link = self._url_folder_format.format(**self._git)
        return self.__sha_get(link)

    def file_update(self, path, old_sha):
        """ Check file hash and download if updated """
        link = self._file_download_request_url(path)
        new_sha, err = self.__sha_get(link + '?format=meta')
        add_header = {'Accept': 'application/vnd.github.v3.raw'}
        return self._pre_download_file(link, path, old_sha, new_sha, err, add_header)

    def file_upload(self, path, git_file_sha):
        """ Upload file to git repository (if sha set - use update method otherwise create) """
        data_binary, err = self._read_file_data(path)
        if err:
            return None, err
        data_coded = base64.b64encode(data_binary).decode('utf-8')
        git_path, link, head = self._file_upload_request_values(path, self._access)
        obj = {
            'message': self._commit_msg.format(path=git_path),
            'content': data_coded,
            'branch': self._git['branch'],
            'sha': git_file_sha,
        }
        req_obj = {'method': 'PUT', 'url': link, 'headers': head, 'data': json.dumps(obj)}

        def fn(x):  # Lambda function to find sha
            return x['commit']['hash']
        return self._file_upload_sha(req_obj, fn)

    def __sha_get(self, link):
        req_obj = {'method': 'GET', 'url': link, 'headers': self._access}
        response, err = self._request(req_obj)
        return (None, err) if err else self.__sha_from_response(response)

    @staticmethod
    def __sha_from_response(response):
        try:
            response = response.json()
            return response['commit']['hash'], None
        except (KeyError, TypeError):
            return None, 'Commit not found in response'
        except ValueError:
            return None, f'Json parse error {response.text}'
