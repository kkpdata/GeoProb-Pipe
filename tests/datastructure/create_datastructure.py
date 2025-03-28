"""Define and create a datastructure and variables for the app"""

from dataclasses import dataclass

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
    VariableName: str
    VariableDescription: str
    VariableUnit: str
    VariableType: str
    VariableDefaulValue: float


@dataclass
class Vakken:
    VakID: int
    Vaknaam: str
    M_van: float
    M_tot: float
    Vaklengte: float
    BodemhoogteVak: float
    Weerstand_C1_mean: float
    Weerstand_C1_vc: float
    Weerstand_C3_mean: float
    Weerstand_C3_vc: float


@dataclass
class Uittredepunten:
    UittredepuntID: int
    X_uitrede: float
    Y_uitrede: float
    Uitredelocatie: str
    Mvalue: float
    VakID: int
    Vaknaam: str
    DIST_L_GEOM: float
    DIST_BUT: float
    DIST_BIT: float
    DIST_L3: float
    HydraLocatieID: str
    WBN: float
    Bodemhoogte: float
    Polderpei: float


@dataclass
class Ondergrondscenarios:
    OndergrondscenarioID: int
    VakID: int
    ScenarioID: int
    ScenarioNaam: str
    ScenarioKans: float
    Top_zand_mean: float
    Top_zand_stdev: float
    gamma_sat_cover_mean: float
    gamma_sat_cover_stdev: float
    d_wvp_mean: float
    d_wvp_stdev: float
    kD_wvp_mean: float
    kD_wvp_vc: float
    k_wvp_mean: float
    k_wvp_stdev: float
    D70_mean: float
    D70_vc: float
