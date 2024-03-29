from core.services.git_interface.git_interface import GitInterface


def test_git_manager():
    repos = [
        {
            'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
            'branch': 'master', 'path': '',
            'sha': None, 'access': {'access_type': 'token', 'token': 'a64a7ef131c0a8823e9f4b8228b86f5c077fd6b9'},
            'file_list': [
                {'path': 'C:/tmp/test-github-no.txt', 'sha': 'fb69b1309df009aa9664e38ed3c467cd3a136003'},
                {'path': 'C:/tmp/test-github.txt', 'sha': ''},
                {'path': 'C:/tmp/test-github-not-found.txt', 'sha': ''},
            ],
        },
        {
            'provider': 'github.com', 'owner': 'meoook', 'name': 'testrepo1',
            'branch': 'master', 'path': '',
            'sha': 'ff5b7030e4a01ee4d8702aec5871959208604108', 'access': None,
            'file_list': [
                {'path': 'C:/tmp/test-github-upload.txt', 'sha': '821c898537855698fc858489e299b439f82e54ea'},
            ],
        },
        {
            'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
            'branch': 'master', 'path': 'Folder1',
            'sha': None, 'access': None,
            'file_list': [
                {'path': 'C:/tmp/test-gitlab-no.txt', 'sha': 'c6097bb6c97cb672bd90b155fe26ea2ddfdbbcb9'},
                {'path': 'C:/tmp/test-gitlab.txt', 'sha': ''},
                {'path': 'C:/tmp/test-gitlab-not-found.txt', 'sha': ''},
            ],
        },
        {
            'provider': 'gitlab.com', 'owner': 'mewooook', 'name': 'testproject',
            'branch': 'master', 'path': 'Folder1',
            'sha': '0fa56b7da081483f01b435a74a41d678823de1ab', 'access': None,
            'file_list': [
                {'path': 'C:/tmp/test-gitlab-upload.txt', 'sha': 'aaa'},
            ],
        },
        {
            'provider': 'bitbucket.org', 'owner': 'mewooook', 'name': 'test',
            'branch': 'master', 'path': 'Folder1',
            'sha': None, 'access': {'access_type': 'oauth', 'token': 'dT3cWh4p3QxvMf4WnG'},
            'file_list': [
                {'path': 'C:/tmp/test-bitbucket-no.txt', 'sha': '1b4430ee417a7c32296424189dc3b93cec6005f0'},
                {'path': 'C:/tmp/test-bitbucket.txt', 'sha': ''},
                {'path': 'C:/tmp/test-bitbucket-not-found.txt', 'sha': ''},
            ],
        },
        {
            'provider': 'bitbucket.org', 'owner': 'mewooook', 'name': 'test',
            'branch': 'master', 'path': 'Folder1',
            'sha': '1b4430ee417a7c32296424189dc3b93cec6005f0', 'access': {'access_type': 'oauth', 'token': 'dT3cWh4p3QxvMf4WnG'},
            'file_list': [
                {'path': 'C:/tmp/test-bitbucket-upload.txt', 'sha': ''},
            ],
        },
    ]

    for repo in repos:
        git = GitInterface()
        print(f'== GO REPO ======= {repo["provider"]} =======')
        try:
            git.repo = repo
            update = git.need_update
        except AssertionError as err:
            print('ERROR', err)
            continue
        print('UPDATE:', f'YES {git.sha}' if update else f'NO {git.sha}')
        if not update:
            print('-- UPLOAD FILE -------------------------')
            filo_hash, err = git.upload_file(repo['file_list'][0]['path'], repo['file_list'][0]['sha'])
            print('UPLOADED', filo_hash, 'Errors:', err)
        else:
            print('-- CHECK FILES -------------------------')
            for filo in repo['file_list']:
                try:
                    filo_sha, file_err = git.update_file(filo['path'], filo['sha'])
                except AssertionError as err:
                    print('ERROR ASSERT', err)
                else:
                    if file_err:
                        print('ERROR FILE', file_err)
                    else:
                        print('SUCCESS:', f'updated {filo_sha}' if filo_sha else 'up to date', '-', filo['path'])
        print(f'== END =========== {repo["provider"]} ======*')


test_git_manager()
