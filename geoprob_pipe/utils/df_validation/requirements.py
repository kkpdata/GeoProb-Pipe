from pandas import Series, DataFrame, to_numeric
import numpy as np
from geoprob_pipe.utils.df_validation.requirement import ValidationRequirement
from typing import List, Optional, Callable, Literal


def is_string(s: Series) -> Series:
    return s.apply(lambda x: isinstance(x, str))


IsString = ValidationRequirement(requirement=is_string, failure_msg="Value in column is not a string (textual).")


def is_in_range(
        left: float, right: float,
        inclusive: Literal["both", "neither", "left", "right"] = "both") -> Callable[[Series], Series]:
    return lambda s: s.between(left, right, inclusive=inclusive)


class IsInRange(ValidationRequirement):
    def __init__(
            self,
            left: float,
            right: float,
            inclusive: Literal["both", "neither", "left", "right"] = "both",
            filters: Optional[Callable[[DataFrame], Series]] = None,
            stop_validation_on_failure: bool = False
    ):
        super().__init__(
            requirement=is_in_range(left=left, right=right, inclusive=inclusive),
            failure_msg=f"Value should be in range {left} to {right} (inclusive={inclusive}).",
            filters=filters,
            stop_validation_on_failure=stop_validation_on_failure)


def is_not_null(s: Series) -> Series:
    return ~(s == "")


def is_null(s: Series) -> Series:
    return (s == "")


def is_in(values: List):
    assert isinstance(values, List)
    return lambda s: s.isin(values)


class IsIn(ValidationRequirement):
    def __init__(
            self, values: List, filters: Optional[Callable[[DataFrame], Series]] = None,
            stop_validation_on_failure: bool = False):
        super().__init__(
            requirement=is_in(values=values), failure_msg=f"Value should be in list {values}.",
            filters=filters, stop_validation_on_failure=stop_validation_on_failure)


def is_integer(s: Series) -> Series:
    return s.apply(lambda x: isinstance(x, (int, np.integer)))


def is_whole_number(s: Series) -> Series:
    s_num = to_numeric(s, errors="coerce")  # De tweede test breekt als er iets anders dan een getal in staan.
    return s_num.notna() & (s_num % 1 == 0)


def is_numeric(s: Series) -> Series:
    s_num = to_numeric(s, errors="coerce")
    return s_num.notna()
