from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from typing import List, TYPE_CHECKING
from pandas import DataFrame
from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class BaseSystemBuilder:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.system_class = ParallelSystemReliabilityCalculation
        self.geoprob_pipe: GeoProbPipe = geoprob_pipe

    def build_instances(self) -> List[ParallelSystemReliabilityCalculation]:

        # project_settings = self.construct_project_settings(df_settings=df_settings)  # TODO: Replace

        # Gather input
        df_expanded = run_expand_input_tables(
            geopackage_filepath=self.geoprob_pipe.input_data.app_settings.geopackage_filepath)

        # Filter vakken (optional)
        to_run_vakken_ids = self.geoprob_pipe.input_data.app_settings.to_run_vakken_ids
        if to_run_vakken_ids is not None:
            df_expanded = df_expanded[df_expanded['vak_id'].isin(to_run_vakken_ids)]

        # Iteration dataframe
        df_unique_combos: DataFrame = df_expanded[["uittredepunt_id", "ondergrondscenario_naam"]].drop_duplicates()

        # Iterate over calculation (unique combos)
        list_calculations = []
        for index, row in df_unique_combos.iterrows():

            # General information
            uittredepunt_id = row["uittredepunt_id"]
            ondergrondscenario_naam = row["ondergrondscenario_naam"]
            vak_id = self.geoprob_pipe.input_data.uittredepunten.uittredepunt(uittredepunt_id=uittredepunt_id).vak_id

            # Collect input for specific calculation
            df_filter = df_expanded[
                (df_expanded["uittredepunt_id"] == row["uittredepunt_id"]) &
                (df_expanded["ondergrondscenario_naam"] == row["ondergrondscenario_naam"])]
            df = df_filter.copy(deep=True)

            # Parse parameter input to list of dictionaries
            df['parameter_input'] = df.apply(
                lambda row2: {**row2['parameter_input'], 'name': row2['parameter_name']}, axis=1)
            calculation_input = df['parameter_input'].values.tolist()

            # Construct calculation
            calc = self.system_class(
                system_variable_distributions=calculation_input,
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

            list_calculations.append(calc)

        return list_calculations
