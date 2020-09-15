

aa = True


def __decor(function):
    def test_func(*args, **kwargs):
        if aa:
            function(*args, **kwargs)
        else:
            print('Error')

    return test_func


@__decor
def test(xx):
    print(f'test data {xx}')


test('bb')

