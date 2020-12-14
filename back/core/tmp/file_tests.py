import os

from core.services.file_interface.file_read_csv import LocalizeCSVReader
from core.services.file_interface.file_read_html import LocalizeHtmlReader
from core.services.file_interface.file_read_ue import LocalizeUEReader
from core.services.file_interface.html_parser import HtmlContextParser
from core.services.file_interface.id_finder import UniqueIDLookUp
from core.services.file_interface.file_scanner import FileScanner


def file_scanner_test():
    scanned_amount = 0
    # my_path = r'C:\Projects\PY\Abby\HELIOS'
    my_path = r'C:\Projects\PY\Abby\HELIOS\ls'

    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if '-ru' in file_name or file_name == 'Ru.po':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            scanned_amount += 1
            print(idxx, file_path, {**info.info})
        else:
            # print(idxx, 'NO NEED TO CHECK', file_name)
            pass
        if scanned_amount > 3:
            print('FINISH')
            break


def fid_finder_test():
    xx = UniqueIDLookUp()
    xx.header = ['xasixdccd', 'asdfsa_IxDdf']
    xx[1] = 1
    xx[2] = 6
    xx.next_row()
    xx[1] = 2
    xx[2] = 7
    xx.next_row()
    xx[1] = 3
    xx[2] = 8
    xx.next_row()
    xx[1] = 4
    xx[2] = 9
    xx[3] = 0
    xx.next_row()
    xx[1] = 5
    xx[2] = 0
    xx.next_row()
    print(xx.header)
    print(xx.formula)
    xx.formula = '+2:5'
    ddd = xx.function
    print(ddd([1, '2', 3, 4, 5]))


def csv_reader_test():
    scanned_amount = 0
    my_path = r'C:\Projects\PY\Abby\HELIOS'
    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if '-ru' in file_name and file_name[-3:] == 'txt':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            scanned_amount += 1
            print(idxx, file_path, {**info.info})
            if not info.error:
                print('READ ROW BY ROW ================================================')
                row_reader = LocalizeCSVReader(info.data, info.codec, info.options)
                print('CHECK REPLACE', next(row_reader)['context'])
                print('REPLACED ROW ===', row_reader.copy_write_mark_items([{'item_number': 10, 'text': 'bugaga'}]))
                for idx, row_data in enumerate(row_reader):
                    print(idx + 1, 'VAL:', row_data)
                    if idx > 4:
                        break  # to long to check
        if scanned_amount > 2:
            print('FINISH')
            break


def ue_reader_test():
    scanned_amount = 0
    my_path = r'C:\Projects\PY\Abby\HELIOS\ls'
    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if file_name[-2:] == 'po':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            scanned_amount += 1
            print(idxx, file_path, {**info.info})
            if not info.error:
                print('READ ROW BY ROW ================================================')
                reader = LocalizeUEReader(info.data, info.codec, info.options)
                print('CHECK REPLACE', next(reader))
                print('REPLACED ROW ===', reader.copy_write_mark_items([{'item_number': 1, 'text': 'bugaga'}]))
                for idx, row_data in enumerate(reader):
                    print(idx + 1, 'VAL:', row_data)
                    if idx > 10:
                        break  # to long to check
        if scanned_amount > 2:
            print('FINISH')
            break


def html_reader_test():
    my_path = r'C:\Projects\PY\Abby\HELIOS\html'
    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if file_name == 'top_list_info2.htm' and file_name[-3:] == 'htm' or file_name[-4:] == 'html':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            print(idxx, file_path, {**info.info})
            if not info.error:
                print('READ ROW BY ROW ================================================')
                reader = LocalizeHtmlReader(info.data, info.codec, info.options)
                for x in reader:
                    print('VALUE', x)
                reader.copy_write_mark_items([{'item_number': 1, 'text': 'bugaga'}])


def html_reader_test2():
    my_path = r'C:\Projects\PY\Abby\HELIOS\html'
    _, _, file_names = next(os.walk(my_path))

    for idxx, file_name in enumerate(file_names):
        if file_name == 'top_list_info2.htm' and file_name[-3:] == 'htm' or file_name[-4:] == 'html':
            file_path = os.path.join(my_path, file_name)
            info = FileScanner(file_path, 'ru')
            print(idxx, file_path, {**info.info})
            if not info.error:
                print('READ ROW BY ROW ================================================')
                html_manager = HtmlContextParser(info.data, info.codec, info.options)
                [print('TREE:', x) for x in html_manager.tree]
                for key in html_manager.data:
                    print(f'VALUE: {key}')
                # reader.copy_write_mark_items([{'item_number': 1, 'text': 'bugaga'}])


if __name__ == '__main__':
    # file_scanner_test()
    # po_lib_test()
    # fid_finder_test()
    # csv_reader_test()
    # ue_reader_test()
    # html_reader_test()
    html_reader_test2()
    # my_path = r'C:\Projects\PY\Abby\HELIOS\Ability-ru.txt'
    # w = r'C:\Projects\PY\Abby\test.txt'
    #
    # filo = open(my_path, 'r', encoding='utf-8')
    # other = open(w, 'w', encoding='utf-8')
    # data = filo.read()
    # for x in data.splitlines():
    #     print(x.encode())
    #     other.write(x + '\n')
