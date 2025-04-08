"""Define and create a datastructure and variables for the app"""

import os
from dataclasses import dataclass

import pandas as pd

# Define the input variables for the functions for Uplift, Heave and Piping
# dist_L_geom: float
# dist_BUT: float
# dist_BIT: float
# L3_geom: float
# mv: float
# pp: float
# top_zand: float
# gamma_sat_cover: float
# gamma_w: float
# kD: float
# D: float
# d70: float
# c1: float
# c3: float
# mu: float
# mh: float
# mp: float
# i_c_h: float
# rc: float
# h: float


@dataclass
class Variables:
    """Class to store a description of the variables used in the model."""

    VaribleID: int
    VariableName: str  # name of the variable
    VariableDescription: str  # description of the variable
    VariableUnit: str  # dimension of the variable
    VariableType: str  # Input, Output, Constant, Calculated
    VariableDistribution: str  # Lognormal, Normal, Deterministic, n.b. CalculationSettings in different class
    Spreidingstype: str  # _mean, _stdev, _vc
    VariableDefaulValue: float
    VariableLowerBound: float
    VariableUpperBound: float


@dataclass
class Vakken:
    VakID: int
    Vaknaam: str
    M_van: float
    M_tot: float
    Vaklengte: float
    bodemhoogte_vak: float
    c1_mean: float
    c1_vc: float
    c3_mean: float
    c3_vc: float


@dataclass
class Uittredepunten:
    UittredepuntID: int
    X_uitrede: float
    Y_uitrede: float
    Uitredelocatie: str
    Mvalue: float
    VakID: int
    Vaknaam: str
    L_intrede: float
    L_but: float
    L_bit: float
    L3: float
    HydraLocatieID: str
    buitenwaterstand: float
    bodemhoogte: float
    polderpeil: float


@dataclass
class Ondergrondscenarios:
    OndergrondscenarioID: int
    VakID: int
    ScenarioID: int
    Scenarionaam: str
    Scenariokans: float
    top_zand_mean: float
    top_zand_stdev: float
    gamma_sat_deklaag_mean: float
    gamma_sat_deklaag_stdev: float
    D_wvp_mean: float
    D_wvp_stdev: float
    kD_wvp_mean: float
    kD_wvp_vc: float
    k_wvp_mean: float
    k_wvp_stdev: float
    d70_mean: float
    d70_vc: float


def create_table_from_dataclass(dataclass):
    """Create a pandas DataFrame from a dataclass instance."""
    # Get the field names and values from the dataclass
    field_names = [field.name for field in dataclass.__dataclass_fields__.values()]
    # field_values = [getattr(dataclass_instance, field) for field in field_names]
    # Create a DataFrame with the field names as columns and the values as a single row
    df = pd.DataFrame(columns=field_names)
    return df


if __name__ == "__main__":
    # Need to creat a excel file with the dataclass instances
    # Create dataframes of the dataclasses
    variable_table = create_table_from_dataclass(Variables)

    filepath_variable_table = "tests/datastructure/variable_definition_generated.xlsx"
    # if file exists, do not create a new file
    if not os.path.exists(filepath_variable_table):
        variable_table.to_excel(
            filepath_variable_table, sheet_name="Variables", index=False
        )
        print(f"Excel file {filepath_variable_table} created.")
    else:
        print(
            f"File {filepath_variable_table} already exists. Not creating a new file."
        )

    vakken_table = create_table_from_dataclass(Vakken)
    uittredepunten_table = create_table_from_dataclass(Uittredepunten)
    ondergrondscenarios_table = create_table_from_dataclass(Ondergrondscenarios)

    filepath_datastructure = "tests/datastructure/example_datastructure.xlsx"

    # Create a dictionary to hold the dataframes
    dataframes = {
        "Vakken": vakken_table,
        "Uittredepunten": uittredepunten_table,
        "Ondergrondscenarios": ondergrondscenarios_table,
    }
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(filepath_datastructure, engine="openpyxl") as writer:
        # Write each dataframe to a different worksheet.
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Excel file {filepath_datastructure} created.")
