# TODO: fix readfile func return annotations
# TODO: fix annotations for to_numeric and to_datetime funcs
# TODO: calls of to_numeric and to_datetime should be kwarg based

import csv
from datetime import datetime
from tabulate import tabulate
from typing import Union, Any, List, Tuple, Dict
from utils.config import DT_FORMAT, INP_DIR
from utils.helpers import issue_custom_warning

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
        issue_custom_warning("Reading file from cache")
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


def filter_data(data: Dict[str, List[Union[int, float, datetime]]],
                min_values: Dict[str, Union[int, float, datetime]],
                max_values: Dict[str, Union[int, float, datetime]]) -> \
        Dict[str, List[Union[int, float, datetime]]]:
    # validating types
    for col_name, col_values in data.items():
        if col_name in min_values and not isinstance(min_values[col_name], type(col_values[0])):
            raise TypeError(f"Invalid type for {col_name} in min_values")
        if col_name in max_values and not isinstance(max_values[col_name], type(col_values[0])):
            raise TypeError(f"Invalid type for {col_name} in max_values")

    # checking in min_values and max_values have same length
    if set(min_values.keys()) != set(max_values.keys()):
        raise ValueError("min_values and max_values should have the same keys")

    # using dictionary comprehension to create filtered_data
    filtered_data = {col: [] for col in data}
    for col_name in min_values:
        min_val = min_values[col_name]
        max_val = max_values[col_name]
        for index, val in enumerate(data[col_name]):
            if min_val <= val <= max_val:
                for col_name_ in data:
                    filtered_data[col_name_].append(data[col_name_][index])
    return filtered_data


def show_data(data_to_show: Dict[str, List[Union[int, float, datetime, str]]],
               tablefmt: str = "simple_outline") -> None:
    table = tabulate(data_to_show, tablefmt=tablefmt, headers="keys", showindex="always")
    print(table)


if __name__ == "__main__":
    # reading and processing data
    inp_data = get_data_from_file(r"C:\Users\Martyniuk Vadym\Desktop\text_data1.txt",
                                  dt_format=DT_FORMAT)
    show_data(inp_data)

    # filtering data
    inp_data = filter_data(inp_data,
                           min_values={"0": datetime.strptime("2019-05-06 10:48:00", DT_FORMAT)},
                           max_values={"0": datetime.strptime("2019-05-06 10:52:00", DT_FORMAT)})
    show_data(inp_data)

    # inp_data = get_data_from_file(r"C:\Users\Martyniuk Vadym\Desktop\solar_data_proccessing-\data\Photovoltaic array A measurements.csv",
    #                               dt_format=DT_FORMAT, header=True)
