import re
from typing import Callable


class UniqueIDLookUp:
    """
    Class to find unique ID field(s) in CSV that returns string formula, also return GetID function from this formula.
    Can also be used to check unique for UE method.
    Usage:
    To find formula:
        # define class
            find_unique_id = UniqueIDLookUp()
        # iterate your lookup array
        ...
            find_unique_id[cow_n] = text
        # before next row - call next row command
            find_unique_id.next_row()
        ...
        # get formula after iterate finish
            lookup_formula = find_unique_id.formula
    To get id from formula
        # define class
            find_unique_id = UniqueIDLookUp()
        # define function to get ID from formula
            find_unique_id.formula = '+2:5'
            get_id_function = find_unique_id.function
        # get ID from items list (row items split)
            unique_id_from_items = get_id_function([1, '2', 3, 4, 5]) # result = '25'
    """

    def __init__(self):
        self.__columns_of_possible_ids: dict[int, any] = {}  # Matrix
        self.__formula: str = ''
        self.__row_amount: int = 1
        self.__variants: list[int] = []
        self.__header: list[str] = []  # Help to choose if several variants

    @property
    def function(self) -> Callable[[list[any]], str]:
        """ Function to get FID from row items """
        assert self.__formula, "formula not set"
        return self.__get_function_from_formula()

    @property
    def formula(self) -> str:
        """ String formula to save in DB - get fid lookup function with it """
        if not self.__formula:
            self.__set_formula()
        return str(self.__formula)

    @formula.setter
    def formula(self, value: str):
        """ Set formula to get fid lookup function """
        self.__formula = str(value)

    @property
    def header(self) -> list[str]:
        """ No need this param, just for setter """
        return self.__header

    @header.setter
    def header(self, value: list[str]):
        """ Set header row to find possible FID column (find 'ID' in row) """
        if isinstance(value, list):
            self.__header = value

    def __setitem__(self, key: int, value: any):
        """ Adding items to matrix [col,row]:value """
        if self.__row_amount == 1:
            self.__columns_of_possible_ids[key] = [value]
        elif key in self.__columns_of_possible_ids:
            self.__columns_of_possible_ids[key].append(value)

    def next_row(self) -> None:
        """ End row trigger for matrix """
        columns = list(self.__columns_of_possible_ids.keys())
        for col_n in columns:
            if len(self.__columns_of_possible_ids[col_n]) != self.__row_amount:
                del self.__columns_of_possible_ids[col_n]
        self.__row_amount += 1

    def __set_formula(self) -> None:
        """ Find string formula to get FID """
        if self.__find_unique_cols():
            variants_amount = len(self.__variants)
            if variants_amount == 1:
                self.__formula = self.__variants[0]
            elif not self.__find_id_in_header():
                self.__formula = self.__find_formula_in_combinations_of_cols()
        else:
            self.__formula = self.__find_formula_in_combinations_of_cols()

    def __find_unique_cols(self) -> bool:
        """ Find columns where all values unique """
        self.__row_amount -= 1
        for col_n, values in self.__columns_of_possible_ids.items():
            # DEBUG: uncomment to check values
            # arr = []
            # [arr.append(x) if x not in arr else print(x) for x in values]
            if len(set(values)) == self.__row_amount:
                self.__variants.append(col_n)
        return bool(self.__variants)

    def __find_id_in_header(self) -> bool:
        if not self.__header:
            return False
        for name in self.__header:
            if re.search(r'([^a-z]?id[^a-z]|[^a-z]id[^a-z]?)', name, re.IGNORECASE):
                self.__formula = self.__header.index(name) + 1
                return True
        for name in self.__header:
            if 'id' in name.lower():
                self.__formula = self.__header.index(name) + 1
                return True
        return False

    def __find_formula_in_combinations_of_cols(self) -> str:
        """ Sum ids in columns pairs to find formula like +1:2 """
        if len(self.__columns_of_possible_ids) < 2:
            return ''
        id_cols = self.__columns_of_possible_ids.copy()
        for col in self.__columns_of_possible_ids:
            new_ids = []
            one_col_ids = id_cols.pop(col)
            for column_number in id_cols:
                name = f'+{col}:{column_number}'
                ids = id_cols[column_number]
                zipped = zip(one_col_ids, ids)
                for col_one_id, col_two_id in zipped:
                    new_ids.append(f'{col_one_id}{col_two_id}')
                if len(set(new_ids)) == self.__row_amount:
                    return name
        return ''

    def __get_function_from_formula(self) -> Callable[[list[any]], str]:
        """ Return function to get FID from row items list by formula """
        str_fm = self.__formula
        if str_fm[0] == '+':
            work_cols = str_fm[1:].split(':')
        else:
            work_cols = [str_fm]

        def return_fn(values: list[any]) -> str:
            data = [str(abs(int(val))) for val in values if str(values.index(val) + 1) in work_cols]
            return ''.join(data)
        return return_fn
