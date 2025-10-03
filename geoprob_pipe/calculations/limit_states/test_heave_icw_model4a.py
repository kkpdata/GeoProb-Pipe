import pytest
from . import heave_icw_model4a


## Get data for testing calc_dh_c function
from pathlib import Path
testset_path = Path(
    Path(__file__).resolve(strict=True).parents[3],
    "tests/testset",
    "testset_limitstate_piping.xlsx",
)

def get_data():
    """Get data for testing calc_dh_c function"""
    import pandas as pd
    data = pd.read_excel(testset_path, sheet_name="Blad1", header=0)
    return data

# define input and output keys for calc_dh_c function
input_keys_calc_z_heave = [
    "L3_geom", # L_achterland 
    "c_1", # c_voorland
    "c_3", # c_achterland
    "DIST_L_GEOM", # L_intrede
    "DIST_BUT", # L_but
    "DIST_BIT", # L_bit
    "pp", # polderpeil
    "h", # buitenwaterstand
    "mv", # mv_exit
    "top_zand", # top_zand
    "kD_WVP", # kD_wvp
    "mh", # modelfactor_h
    "i_c_h", # i_c_h
    "D_zand", # D_wvp
    ]

output_key_calc_z_heave = [
    "Z_h", # z_h
    "L1", # lengte_voorland
    "r", # r_exit
    "pot_exit", # phi_exit
    "h_exit", # h_exit
    "Dcover", # d_deklaag  
    "i_optredend", # i_exit
    ] 

# global variables
G = 9.81  # m/s^2
V = 1.33e-6  # m^2/s
ETA = 0.25  # [-]
THETA = 37.0  # grd
GAMMA_KORREL = 26.0  # kN/m^3
D70_M = 2.08e-4  # m

#setup test construct
data_calc_z_heave = get_data()
inputs_calc_z_heave = data_calc_z_heave[input_keys_calc_z_heave].to_dict(orient="records")
expected_outputs_calc_z_heave = data_calc_z_heave[output_key_calc_z_heave].to_dict(orient="records")

@pytest.mark.parametrize("inputs, expected", zip(inputs_calc_z_heave, expected_outputs_calc_z_heave))
def test_calc_z_heave(inputs, expected):
    """Test calc_dh_c function with multiple test cases from excel file"""
    result = heave_icw_model4a.z_heave(
        L_achterland=inputs["L3_geom"],
        c_voorland=inputs["c_1"],
        c_achterland=inputs["c_3"],
        L_intrede=inputs["DIST_L_GEOM"],
        L_but=inputs["DIST_BUT"],
        L_bit=inputs["DIST_BIT"],
        polderpeil=inputs["pp"],
        buitenwaterstand=inputs["h"],
        mv_exit=inputs["mv"],
        top_zand=inputs["top_zand"],
        kD_wvp=inputs["kD_WVP"],
        modelfactor_h=inputs["mh"],
        i_c_h=inputs["i_c_h"],
        D_wvp=inputs["D_zand"],
    )
    assert result[0] == pytest.approx(expected["Z_h"], 0.01)
    assert result[1] == pytest.approx(expected["L1"], 0.01)
    assert result[2] == pytest.approx(expected["r"], 0.01)
    assert result[3] == pytest.approx(expected["pot_exit"], 0.01)
    assert result[4] == pytest.approx(expected["h_exit"], 0.01)
    assert result[5] == pytest.approx(expected["Dcover"], 0.01)
    assert result[6] == pytest.approx(expected["i_optredend"], 0.01)
