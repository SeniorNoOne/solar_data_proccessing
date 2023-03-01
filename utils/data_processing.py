# TODO: fix readfile func return annotations
# TODO: fix annotations for to_numeric and to_datetime funcs
# TODO: calls of to_numeric and to_datetime should be kwarg based

import csv
from datetime import datetime
from typing import Union, List, Tuple, Dict


# global cache variable to prevent reprocessing big files
OPENED_FILES = {}


def read_file(filename: str, sep: str = ",", header: bool = False,
              col_names: Union[List[str], Tuple[str, ...]] = None) -> Dict[str, List[str]]:
    # opening file in read mode
    with open(filename, "r") as inp_file:
        reader = csv.reader(inp_file, delimiter=sep)

        # if csv has a header and col_names were not specified
        if header and not col_names:
            col_names = next(reader)
        # if csv has no header and col_names were not specified
        elif not header and not col_names:
            col_names = [str(i) for i in range(len(next(reader)))]
            inp_file.seek(0)

        # validation of col_names
        if not isinstance(col_names, (list, tuple)) or \
                not all(isinstance(name, str) for name in col_names):
            raise ValueError("col_names should be a list or tuple of strings")

        # reading data from file and converting it using default_type
        data = {key: [] for key in col_names}
        for line in reader:
            for key, val in zip(col_names, line):
                data[key].append(val)
    return col_names, data


def to_numeric(col: List[str],
               default: Union[int, float, None] = None,
               d_type: Union[type[int], type[float]] = float,
               use_next: bool = True) -> List[Union[int, float]]:
    # iterating over given column
    for index, val in enumerate(col):
        # converting val to specified in to_type type if val is not empty
        if val:
            col[index] = d_type(val)
        # otherwise processing empty record
        else:
            # first we look for prev or next not empty record that will replace empty record
            # if there is no such value we replace it with default value
            entry = find_first_entry(col, index, use_next)
            col[index] = d_type(entry) if entry else default
    return col


def to_dt(col: List[str],
          default: datetime = datetime.now(),
          dt_format: str = "", use_next: bool = True) -> List[datetime]:
    # checking dt_format
    if not dt_format:
        raise ValueError("dt_format should be specified")

    # iterating over given column
    for index, val in enumerate(col):
        # if val is not empty - converting it to datetime using dt_format
        if val:
            col[index] = datetime.strptime(val, dt_format)
        else:
            # first we look for prev or next not empty record that will replace empty record
            # if there is no such value we replace it with default value
            entry = find_first_entry(col, index, use_next)
            col[index] = entry if entry else default
    return col


def find_first_entry(iterable: Union[list[str], tuple[str, ...]],
                     start_index: int,
                     forward: bool = True) -> Union[str, None]:
    if start_index < 0 or start_index >= len(iterable):
        raise ValueError("start_index is out of range")
    iterable = iterable if forward else reversed(iterable)
    for item in iterable[start_index:]:
        if item:
            return item


def is_col_numeric(col: Union[List[str], Tuple[str, ...]], test_size: int = 10):
    non_empty_records = []
    for item in col:
        if item:
            item = item.replace(".", "", 1).isdigit()
            non_empty_records.append(item)
            test_size -= 1
        if test_size == 0:
            break
    return all(non_empty_records)


def get_data_from_file(filename: str, sep: str = ",", header: bool = False,
                       col_names: Union[List[str], Tuple[str, ...]] = None,
                       numeric_default: Union[int, float, None] = None,
                       numeric_dtype: Union[type[int], type[float]] = float,
                       dt_default: datetime = datetime.now(),
                       dt_format: str = "",
                       use_next: bool = True) -> Dict[str, List[Union[int, float, datetime]]]:
    if filename in OPENED_FILES:
        return OPENED_FILES[filename]
    else:
        # reading raw data from file
        col_names, data = read_file(filename, sep, header, col_names)

        # determining which columns are numeric
        is_col_numeric_ = [is_col_numeric(data[col]) for col in data]
        for index, col_name in enumerate(col_names):
            if is_col_numeric_[index]:
                data[col_name] = to_numeric(data[col_name], numeric_default,
                                            numeric_dtype, use_next)
            else:
                data[col_name] = to_dt(data[col_name], dt_default, dt_format, use_next)
        OPENED_FILES[filename] = data
        return data


if __name__ == "__main__":
    data = get_data_from_file(r"C:\Users\Martyniuk Vadym\Desktop\text_data1.txt",
                              dt_format="%Y-%m-%d %H:%M:%S")
