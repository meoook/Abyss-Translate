""" For this class and it's "extends" classes - all open methods(not getters) return (value, err) """

import re

from core.services.git_interface.git_providers import GitHubConnect, GitLabConnect, BitBucketConnect

# TODO: remake by django.http.requests ?

KNOWN_PROVIDERS = {
    'github.com': GitHubConnect,
    'bitbucket.org': BitBucketConnect,
    'gitlab.com': GitLabConnect,
}
REPO_CHECK_KEYS = ('provider', 'owner', 'name', 'path', 'branch', 'sha', 'access')


class GitInterface:
    """ Class to work with git repositories - GitHub, GitLab, BitBucket (file_manager and folder_manager subclass) """

    def __init__(self):
        self.__repo = None
        self.__sha = None
        self.__git = None
        self.__url = None

    @property
    def repo(self):
        """ To get repo object from parsed URL """
        return self.__repo

    @repo.setter
    def repo(self, value):
        """ Init repository object """
        assert isinstance(value, dict), f'Wrong type of repository object: {type(value)}'
        assert all(k in value for k in REPO_CHECK_KEYS), 'Not a valid repository object'
        assert value['provider'] in KNOWN_PROVIDERS, f'Git provider {value["provider"]} not configured'
        self.__repo = value
        self.__git = KNOWN_PROVIDERS[value['provider']](value)
        self.__url = self.__git.url_repo_http

    @property
    def url(self):
        """ Repository HTTP URL """
        return self.__url

    @url.setter
    def url(self, link):
        """ Create repository object from URL """
        # FIXME: folder names with special chars
        assert isinstance(link, str), f'URL must be string but: {type(link)}'
        url_items = re.match(r'^http[s]?://([^/]+)/(\w+)/(\w+)(?:/(?:tree|src|-/tree)/(\w+)/?)?(.+)?', link)
        assert url_items, f'Repo URL parse error: {link}'
        self.repo = {
            'provider': url_items.group(1), 'owner': url_items.group(2), 'name': url_items.group(3),
            'branch': url_items.group(4) if url_items.group(4) else 'master',
            'path': self.__path_fix(url_items.group(5)) if url_items.group(5) else '',
            'sha': None, 'access': None,
        }

    @property
    def sha(self):
        """ Repository object new hash - connect to repo if not set """
        return self.__sha if self.__sha else self.__get_repo_sha()

    @property
    def need_update(self):
        """ Repository object update status - connect to repo if sha not set """
        if self.sha:  # If not set - connecting and get hash
            return self.__sha != self.__repo['sha']
        return False

    def update_file(self, path, old_sha):
        """ Get and check new hash and download if need to update """
        assert self.repo, 'Repository object not set'
        assert isinstance(path, str), f'Wrong type for path: {type(path)}'
        assert isinstance(old_sha, str), f'Wrong type for hash: {type(old_sha)}'
        return self.__git.file_update(path, old_sha)  # file new hash and error state

    def upload_file(self, path, git_sha=None):
        """ Upload file to git repository (sha here can be not real hash but flag to create or update file) """
        assert self.repo, 'Repository object not set'
        assert isinstance(path, str), f'Wrong type for path: {type(path)}'
        assert isinstance(git_sha, str), f'Wrong type for hash: {type(git_sha)}'
        return self.__git.file_upload(path, git_sha)

    def __get_repo_sha(self):
        """ Check access and exist status and set hash for repository object """
        assert self.__git, 'Git provider not set'
        new_hash, err = self.__git.repo_get_sha()
        assert new_hash, err  # Network error
        self.__sha = new_hash
        return new_hash

    @staticmethod
    def __path_fix(full_path):
        """ Remove filename from path if it's found """
        path_items = re.match(r'^(.+)/(?:[^/\s]+\.[^/\s]+)?$', full_path)
        return path_items.group(1) if path_items else full_path
