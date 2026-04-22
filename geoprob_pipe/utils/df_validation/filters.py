from typing import List
from pandas import DataFrame, Series


def is_in(column: str, values: List):
    def filter_def(df: DataFrame) -> Series:
        return df[column].isin(values)
    return filter_def
