from pandas import Series, DataFrame
import numpy as np
from geoprob_pipe.utils.df_validation.requirement import ValidationRequirement
from typing import List, Optional, Callable


def is_string(s: Series) -> Series:
    return s.apply(lambda x: isinstance(x, str))
# TODO: Hoe krijg ik pre-defined failure messages voor dit soort simpele functies.


IsString = ValidationRequirement(requirement=is_string, failure_msg="Value in column is not a string (textual).")


def is_in(values: List):
    assert isinstance(values, List)
    return lambda s: s.isin(values)


def is_not_null(s: Series) -> Series:
    return s.notna()


class IsIn(ValidationRequirement):
    def __init__(
            self, values: List, df_filter: Optional[Callable[[DataFrame], Series]] = None,
            stop_validation_on_failure: bool = False):
        super().__init__(
            requirement=is_in(values=values), failure_msg=f"Value should be in list {values}.",
            df_filter=df_filter, stop_validation_on_failure=stop_validation_on_failure)


def is_integer(s: Series) -> Series:
    return s.apply(lambda x: isinstance(x, (int, np.integer)))




