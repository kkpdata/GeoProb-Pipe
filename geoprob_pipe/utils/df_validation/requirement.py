from typing import Callable, Optional
from pandas import DataFrame, Series
from uuid import uuid4


class ValidationRequirement:

    def __init__(
            self,
            requirement: Callable[[Series], Series],
            failure_msg: str,
            filters: Optional[Callable[[DataFrame], Series]] = None,
            stop_validation_on_failure: bool = False,
    ):
        self.requirement = requirement
        self.filters = filters
        self.failure_msg = failure_msg
        self.stop_validation_on_failure: bool = stop_validation_on_failure

    def validate(self, df: DataFrame, column: str) -> DataFrame:
        initial_columns = list(df.columns)

        # Start mask
        mask = Series(True, index=df.index)
        if self.filters is not None:
            mask &= self.filters(df)

        # Perform validation
        valid = self.requirement(df[column])

        # Limit only to failed columns
        invalid_mask = mask & ~valid
        df_result: DataFrame = df.loc[invalid_mask].copy()

        # Rename columns (to prevent conflicts with failure information)
        if "failure_msg" in df_result.columns:
            df_result = df_result.rename(columns={"failure_msg": f"failure_msg_{uuid4().__str__()}"})
        if "column" in df_result.columns:
            df_result = df_result.rename(columns={"column": f"column_{uuid4().__str__()}"})

        # Append failure information
        df_result["failure_msg"] = self.failure_msg
        df_result["column"] = column

        # Return failure messages
        return_column_order = ["failure_msg", "column"]
        return_column_order.extend(initial_columns)
        return df_result[return_column_order]
