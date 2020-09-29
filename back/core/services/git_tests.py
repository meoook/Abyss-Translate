from core.services.git_manager import GitManage


def test_git_manager():
    repos = [
        # {
        #     'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
        #     'branch': 'master', 'path': 'Test',
        #     'hash': None, 'access': None,
        #     'file_list': [
        #         {'path': 'C:/tmp/error_github.txt', 'name': 'new.txt', 'hash': '6d1280d85312042a9a3964bf2e34382a999e171b'},
        #         {'path': 'C:/tmp/test_file_github.txt', 'name': 'test_file.txt', 'hash': ''},
        #         {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': '2ef267e25bd6c6a300bb473e604b092b6a48523b'},
        #     ],
        # },
        # {
        #     'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
        #     'branch': 'master', 'path': 'Test',
        #     'hash': 'a76f5aa21175789086fd6f83b258014c4dc96209', 'access': None,
        #     'file_list': [
        #         {'path': 'C:/tmp/error_github.txt', 'name': 'new.txt', 'hash': ''},
        #         {'path': 'C:/tmp/err_github.txt', 'name': 'test_file.txt', 'hash': '2ef267e25bd6c6a300bb473e604b092b6a48523b'},
        #
        #     ],
        # },
        # {
        #     'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
        #     'branch': 'master', 'path': 'Folder1',
        #     'hash': None, 'access': None,
        #     'file_list': [
        #         {'path': 'C:/tmp/error_gitlab.txt', 'name': '_csv.txt', 'hash': '6b882514cbadfceb1775a0347ffa2d321e7b8297'},
        #         {'path': 'C:/tmp/test_file_gitlab.txt', 'name': 'test_file.txt', 'hash': ''},
        #         {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': '54d622dd730f79aa5b8d2582bb5fb2cc6f92bfa4'},
        #     ],
        # },
        # {
        #     'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
        #     'branch': 'master', 'path': 'Folder1',
        #     'hash': '72930c112a2a1b3e634321cf107192fc85106081', 'access': None,
        #     'file_list': [
        #         {'path': 'C:/tmp/error_github.txt', 'name': '_csv.txt', 'hash': ''},
        #         {'path': 'C:/tmp/err_github.txt', 'name': 'test_file.txt', 'hash': '54d622dd730f79aa5b8d2582bb5fb2cc6f92bfa4'},
        #
        #     ],
        # },
        {
            'provider': 'bitbucket.org', 'owner': 'meokok', 'name': 'test',
            'branch': 'master', 'path': 'Folder1',
            'hash': None, 'access': None,
            'file_list': [
                {'path': 'C:/tmp/error_bitbucket.txt', 'name': 'csv.txt', 'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa'},
                {'path': 'C:/tmp/test_file__bitbucket.txt', 'name': 'test_file.txt', 'hash': ''},
                {'path': 'C:/tmp/not_found.txt', 'name': 'not_found.txt', 'hash': ''},
            ],
        },
        # {
        #     'provider': 'bitbucket.org', 'owner': 'meokok', 'name': 'test',
        #     'branch': 'master', 'path': 'Folder1',
        #     'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa', 'access': None,
        #     'file_list': [
        #         {'path': 'C:/tmp/error_bitbucket.txt', 'name': 'csv.txt', 'hash': ''},
        #         {'path': 'C:/tmp/err_bitbucket.txt', 'name': 'test_file.txt', 'hash': '0b6c4d34f4658341164d90e1d8c2c6deb61c2cfa'},
        #     ],
        # },
    ]

    for repo in repos:
        git = GitManage()
        git.repo = repo
        print('==X==================================')
        # if git.sha:
        #     print(git.sha)
        #     print('Need update:', 'YES' if git.need_update else 'NO')
        #     if git.need_update:
        #         # updated = git.update_files(repo['file_list'])
        #         # [print(f'File: {x["name"]} ({x["hash"]}) Updated: {"YES" if x["updated"] else "NO"} with err: {x["err"]}') for x in updated]
        #         print('==Y==================================')
        #         filo_hash = git.upload_file(path=repo['file_list'][1]['path'],
        #                                     git_name='test-en.txt',
        #                                     git_hash=repo['file_list'][2]['hash'])
        #         if filo_hash:
        #             print('Success', filo_hash)
        #         else:
        #             print('Error', git.error)
        # else:
        #     print(git.error)


test_git_manager()








# Test git_formatters
# import requests
# def test_formatters():
#
#     repos = [
#         {
#             'parser': GitHubFormatter, 'owner': 'meoook', 'name': 'testrepo1',
#             'branch': 'master', 'path': 'Test', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Accept': 'application/vnd.github.VERSION.object'},
#         },
#         {
#             'parser': GitHubFormatter, 'owner': 'meoook', 'name': 'testrepo1',
#             'branch': 'master', 'path': 'Test/new.txt', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Accept': 'application/vnd.github.VERSION.object'},
#         },
#         {
#             'parser': GitLabFormatter, 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
#         },
#         {
#             'parser': GitLabFormatter, 'owner': 'mewooook', 'name': 'testproject',
#             'branch': 'master', 'path': 'Folder1/_csv', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk'},
#         },
#         {
#             'parser': BitBucketFormatter, 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1', 'as_file': False,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Content-type': 'application/json'},
#         },
#         {
#             'parser': BitBucketFormatter, 'owner': 'meokok', 'name': 'test',
#             'branch': 'master', 'path': 'Folder1/csv.txt', 'as_file': True,
#             'access': {'PRIVATE-TOKEN': 'ZocaYQAp9UYd18wk1Psk', 'Content-type': 'application/json'},
#         },
#     ]
#
#     for repo in repos:
#         git = repo["parser"]()
#         url = git.url_create(repo, as_file=repo["as_file"])
#         print('url', url)
#         resp = requests.get(url, headers=repo['access'])
#         if resp.status_code == requests.codes.ok:
#             print(git.data_from_resp(resp, as_file=repo["as_file"]))
#         else:
#             print(git.error_from_resp(resp))
