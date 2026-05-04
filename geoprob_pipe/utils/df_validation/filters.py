from typing import List, Callable
from pandas import DataFrame, Series
import operator
from functools import reduce


def is_in(column: str, values: List):
    def filter_def(df: DataFrame) -> Series:
        return df[column].isin(values)
    return filter_def


def is_null(column: str):
    def filter_def(df: DataFrame) -> Series:
        return df[column].isna()
    return filter_def


FilterFn = Callable[[DataFrame], Series]

def combine(*filters: FilterFn, op=operator.and_) -> FilterFn:
    """ Combine multiple filters. """
    def combined(df: DataFrame) -> Series:
        return reduce(op, (f(df) for f in filters))
    return combined
