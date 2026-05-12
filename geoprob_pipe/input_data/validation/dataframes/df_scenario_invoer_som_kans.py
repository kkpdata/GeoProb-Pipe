from typing import List
from geoprob_pipe.input_data.validation.dataframes.validation_objects import FailureQuery
from pandas import DataFrame


def _df_scenario_group_sum_kans(df: DataFrame) -> DataFrame:
    df_grouped: DataFrame = df.groupby(["vak_id"], as_index=False)["kans"].sum()
    df_grouped = df_grouped.rename(columns={"kans": "som_kans"})
    df_grouped["som_kans"] = df_grouped["som_kans"].round(3)
    return df_grouped


FAILURE_QUERIES: List[FailureQuery] = [
    FailureQuery(
        query="som_kans != 1.0",
        msg="In de tabel 'Scenario invoer' moet de som van de kansen gelijk zijn aan 1.0 (100%). "
            "Dit is niet het geval voor dit vak."
    ),
]
