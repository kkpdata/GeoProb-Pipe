from typing import List
from pandas import DataFrame
import os
from dataclasses import dataclass
from geoprob_pipe.utils.validation_messages import BColors


@dataclass
class FailureQuery:
    query: str
    msg: str


class DataFrameQueryValidation:

    def __init__(self, df: DataFrame, failure_queries: List[FailureQuery]):
        self.df = df
        self.failure_queries = failure_queries

    def validate(self, export_dir: str, label_humanized: str) -> bool:
        for failure_query in self.failure_queries:

            # Assess
            df_failure_rows: DataFrame = self.df.query(failure_query.query)
            df_failure_rows = df_failure_rows.copy(deep=True)

            # Continue if no failures
            if df_failure_rows.__len__() == 0:
                continue

            # Prepare dataframe for export
            current_columns = df_failure_rows.columns
            new_column_order = ["validation_msg", "tabel"]
            new_column_order.extend(current_columns)
            df_failure_rows['validation_msg'] = failure_query.msg
            df_failure_rows['tabel'] = label_humanized
            df_failure_rows = df_failure_rows[new_column_order]

            # Report back
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, "df_failure_rows.xlsx")
            if os.path.exists(export_path):
                os.remove(export_path)
            df_failure_rows.to_excel(export_path, index=False)
            print(f"{BColors.WARNING}Validatie is (voortijdig) beëindigd omdat er {df_failure_rows.__len__()} "
                  f"validatie issues voor de '{label_humanized}'-tabel zijn gevonden. De gedetailleerde lijst is "
                  f"geëxporteerd naar onderstaande locatie. Los deze issues s.v.p. eerst op. \n"
                  f"{export_path}{BColors.ENDC}")
            return False

        return True
