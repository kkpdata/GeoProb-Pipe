from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from typing import List, TYPE_CHECKING, Tuple
from geoprob_pipe.utils.validation_messages import BColors
from pandas import DataFrame, Series
import sqlite3
from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _gather_variable_correlations(geopackage_filepath: str) -> List[Tuple[str, str, float]]:
    """ Input originally from the input Excel-file. It defines per combination of two parameters the correlation; a
    value between 0.0 (no correlation) and 1.0 (fully correlated). By default, no correlation is specified for parameter
    combinations, i.e. the probabilistic library automatically assigns 0.0 as correlation for the combination. The
    correlation applies for the entire trajectory.

    TODO: This setup applies for the entire trajectory. In future versions of the code the user should be able to
     assign the correlation on vak, scenario and uittredepunten level.

    :return:
    """

    try:
        conn = sqlite3.connect(geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute(f"""
SELECT parameter_a, parameter_b, correlation FROM correlatie_invoer WHERE correlation <> 0.0;
""")
        rows = cursor.fetchall()  # This will be a list of tuples
        conn.close()
        return rows
    except sqlite3.OperationalError:
        return []


def _gather_calculation_input(df_expanded: DataFrame, uittredepunt_id: int, ondergrondscenario_naam: str) -> List:

    # Collect input for specific calculation
    df_filter = df_expanded[
        (df_expanded["uittredepunt_id"] == uittredepunt_id) &
        (df_expanded["ondergrondscenario_naam"] == ondergrondscenario_naam)]
    df = df_filter.copy(deep=True)

    # Parse parameter input to list of dictionaries
    df['parameter_input'] = df.apply(
        lambda row2: {**row2['parameter_input'], 'name': row2['parameter_name']}, axis=1)
    return df['parameter_input'].values.tolist()


def _generate_single_calculation(
        row_calculation_metadata: Series, vak_id: int,
        df_expanded: DataFrame, system_class,
        variable_correlations: List[Tuple[str, str, float]]
) -> ParallelSystemReliabilityCalculation:

    # General information
    uittredepunt_id = row_calculation_metadata["uittredepunt_id"]
    ondergrondscenario_naam = row_calculation_metadata["ondergrondscenario_naam"]

    # Construct calculation
    calculation_input = _gather_calculation_input(
        df_expanded=df_expanded, uittredepunt_id=uittredepunt_id,
        ondergrondscenario_naam=ondergrondscenario_naam
        )
    calc = system_class(
        system_variable_distributions=calculation_input,
        system_variable_correlations=variable_correlations,
        # project_settings=...
    )
    calc.metadata["uittredepunt_id"] = uittredepunt_id
    calc.metadata["ondergrondscenario_naam"] = ondergrondscenario_naam
    calc.metadata["vak_id"] = vak_id
    metadata_summary = {
        "uittredepunt_id": uittredepunt_id,
        "ondergrondscenario_naam": ondergrondscenario_naam,
        "vak_id": vak_id}
    calc.validation_messages.about = f"Calculation {metadata_summary}"

    return calc


class BaseSystemBuilder:

    def __init__(self,
                 geopackage_filepath: str,
                 to_run_vakken_ids: list[int]):
        self.system_class = ParallelSystemReliabilityCalculation
        self.geopackage_filepath = geopackage_filepath

        # Gather input
        df_expanded = run_expand_input_tables(
            geopackage_filepath=self.geopackage_filepath)

        # Filter vakken (if only selection needs to run)
        if to_run_vakken_ids is not None:
            df_expanded = df_expanded[
                df_expanded['vak_id'].isin(to_run_vakken_ids)
                ]
        self.df_expanded = df_expanded

    def setup_iteration_df(self) -> DataFrame:
        # Iteration dataframe
        df_unique_combos: DataFrame = self.df_expanded[
            ["uittredepunt_id", "ondergrondscenario_naam", "vak_id"]
            ].drop_duplicates()
        return df_unique_combos

    def build_instance(
        self, row_unique
            ) -> ParallelSystemReliabilityCalculation:

        # Gather variable correlations
        variable_correlations: List[Tuple[str, str, float]] = (
            _gather_variable_correlations(self.geopackage_filepath))
        # TODO: Should be made uittredepunt/vak specific in future versions of the code. For now only for the entire
        #  trajectory.

        calc = (_generate_single_calculation(
            row_calculation_metadata=row_unique,
            vak_id=row_unique["vak_id"],
            df_expanded=self.df_expanded,
            system_class=self.system_class,
            variable_correlations=variable_correlations
        ))

        return calc
