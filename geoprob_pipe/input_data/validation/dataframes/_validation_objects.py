from typing import List, Optional
from pandas import DataFrame
from pandera.pandas import DataFrameSchema
from pandera.errors import SchemaErrors
import json
import os
from geoprob_pipe.utils.loggers import BColors


class ValidationSchema:

    def __init__(
            self, schema: DataFrameSchema, label_humanized: str, query: Optional[str] = None):
        """

        :param schema:
        :param label_humanized: Humanreadable label of this validation schema.
        :param query: Optional argument that will be used to query/filter the dataframe.
        """

        # Input arguments
        self.schema = schema
        self.label_humanized = label_humanized
        self.query = query

        # Placeholders
        self._df_failure_cases: Optional[DataFrame] = None

    @property
    def valid(self) -> bool:
        return self._df_failure_cases is None

    @staticmethod
    def _cleanup_dataframe(df_failure_cases: DataFrame) -> DataFrame:
        df_failure_cases = df_failure_cases.rename(columns={"index": "row_index"})
        return df_failure_cases

    @staticmethod
    def _attach_failure_row(df_failure_cases: DataFrame, df: DataFrame) -> DataFrame:
        df_failure_cases["row"] = ""
        for index, row in df_failure_cases.iterrows():
            if row['row_index'] is None:
                continue
            df_failure_cases.loc[index, "row"] = json.dumps(df.loc[row["row_index"]].to_dict())
        return df_failure_cases

    def _apply_query(self, df: DataFrame) -> DataFrame:
        """ Applies the query to the dataframe, if a query is specified. """
        if self.query is None:
            return df
        return df.query(self.query)

    def validate(self, df: DataFrame):
        df = self._apply_query(df=df)  # If query is specified
        try:
            _ = self.schema.validate(df, lazy=True)
        except SchemaErrors as e:
            df_failure_cases: DataFrame = e.failure_cases
            df_failure_cases = df_failure_cases.sort_values(by=["index"])
            df_failure_cases = self._cleanup_dataframe(df_failure_cases=df_failure_cases)
            df_failure_cases = self._attach_failure_row(df_failure_cases=df_failure_cases, df=df)
            self._df_failure_cases = df_failure_cases

    def report_and_export(self, export_dir: str, df_label: str):

        if self.valid:
            print(f"Validation schema for dataframe with label '{self.label_humanized}' is valid. Nothing to report.")
            return

        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, "validation_input_tables.xlsx")
        if os.path.exists(export_path):
            os.remove(export_path)
        self._df_failure_cases.to_excel(export_path)
        print(f"{BColors.WARNING}Validatie is (voortijdig) beëindigd omdat er {self._df_failure_cases.__len__()} "
              f"validatie issues voor de {df_label}-tabel zijn gevonden. De gedetailleerde lijst is geëxporteerd "
              f"naar onderstaande locatie. Los deze issues s.v.p. eerst op. \n"
              f"{export_path}{BColors.ENDC}")


class DataFrameValidation:

    def __init__(self, schemas: List[ValidationSchema], label: str, label_humanized: Optional[str] = None):
        """

        :param schemas:
        :param label: Label of this dataframe validation.
        :param label_humanized: Humanreadable version of the label.
        """
        self.schemas: List[ValidationSchema] = schemas
        self.label = label
        self.label_humanized = label_humanized
        self.valid: Optional[bool] = None

    def validate(self, df: DataFrame, export_dir: str):
        print(f"Starting validation for dataframe {self.label_humanized} ({self.label}).")
        for index, schema in enumerate(self.schemas):
            print(f"   {index+1}/{self.schemas.__len__()}   -   {schema.label_humanized}")
            schema.validate(df=df)

            if not schema.valid:
                label = self.label
                if self.label_humanized is not None:
                    label = self.label_humanized
                schema.report_and_export(export_dir=export_dir, df_label=label)
                self.valid = False
                return  # Stop validation, such that user can fix current validation issues first

        self.valid = True
