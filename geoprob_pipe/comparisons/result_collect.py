import sqlite3
import pandas as pd


class ComparisonCollecter:
    def __init__(self, geopackage_filepath_1: str, geopackage_filepath_2: str):
        self.geopackage_filepath_1 = geopackage_filepath_1
        self.geopackage_filepath_2 = geopackage_filepath_2
        self.name_1 = self.geopackage_filepath_1.split("\\")[-1].split(".")[0]
        self.name_2 = self.geopackage_filepath_2.split("\\")[-1].split(".")[0]

        # Placeholders
        self.df1_beta_scenarios: pd.DataFrame
        self.df1_beta_limit_states: pd.DataFrame
        self.df1_beta_uittredepunten: pd.DataFrame

        self.df2_beta_scenarios: pd.DataFrame
        self.df2_beta_limit_states: pd.DataFrame
        self.df2_beta_uittredepunten: pd.DataFrame

        # logic
        self._load_result_data_from_geopackage()

    def _load_result_data_from_geopackage(self):
        # TODO Must Groot Nu Ensure dataframe are the same size and are
        # based on the same points in geometry.
        conn_1 = sqlite3.connect(self.geopackage_filepath_1)
        conn_2 = sqlite3.connect(self.geopackage_filepath_2)

        self.df1_beta_limit_states = pd.read_sql(
            "SELECT * FROM beta_limit_states;", conn_1
            )
        self.df2_beta_limit_states = pd.read_sql(
            "SELECT * FROM beta_limit_states;", conn_2
            )
        self.df1_beta_scenarios = pd.read_sql(
            "SELECT * FROM beta_scenarios;", conn_1
            )
        self.df2_beta_scenarios = pd.read_sql(
            "SELECT * FROM beta_scenarios;", conn_2
            )
        self.df1_beta_uittredepunten = pd.read_sql(
            "SELECT * FROM beta_uittredepunten;", conn_1
            )
        self.df2_beta_uittredepunten = pd.read_sql(
            "SELECT * FROM beta_uittredepunten;", conn_2
            )
        conn_1.close()
        conn_2.close()
