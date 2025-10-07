import pytest
from . import uplift_icw_model4a


## Get data for testing
from pathlib import Path
testset_path = Path(
    Path(__file__).resolve(strict=True).parents[3],
    "tests/testset",
    "testset_limitstate_piping.xlsx",
)

def get_data():
    """Get data for testing"""
    import pandas as pd
    data = pd.read_excel(testset_path, sheet_name="Blad1", header=0)
    return data

# define input and output keys
input_keys_calc_z_uplift= [
    "L3_geom", # L_achterland 
    "c_1", # c_voorland
    "c_3", # c_achterland
    "pp", # polderpeil
    "h", # buitenwaterstand
    "DIST_L_GEOM", # L_intrede
    "DIST_BUT", # L_but
    "DIST_BIT", # L_bit
    "mv", # mv_exit
    "top_zand", # top_zand
    "kD_WVP", # kD_wvp
    "mu", # modelfactor_u
    "gamma_w", # gamma_water
    "gamma_sat_cover", # gamma_sat_deklaag
    "D_zand", # D_wvp
    ]

output_key_calc_z_uplift = [
    "Z_u", # z_h
    "L1", # lengte_voorland
    "r", # r_exit
    "pot_exit", # phi_exit
    "h_exit", # h_exit
    "Dcover", # d_deklaag  
    "d_pot_cu", # i_exit
    ] 

# global variables
G = 9.81  # m/s^2
V = 1.33e-6  # m^2/s
ETA = 0.25  # [-]
THETA = 37.0  # grd
GAMMA_KORREL = 26.0  # kN/m^3
D70_M = 2.08e-4  # m

#setup test construct
data_calc_z_uplift= get_data()
inputs_calc_z_uplift = data_calc_z_uplift[input_keys_calc_z_uplift].to_dict(orient="records")
expected_outputs_calc_z_uplift = data_calc_z_uplift[output_key_calc_z_uplift].to_dict(orient="records")

@pytest.mark.parametrize("inputs, expected", zip(inputs_calc_z_uplift, expected_outputs_calc_z_uplift))
def test_calc_z_uplift(inputs, expected):
    """Test calc_dh_c function with multiple test cases from excel file"""
    result = uplift_icw_model4a.z_uplift(
        L_achterland=inputs["L3_geom"],
        c_voorland=inputs["c_1"],
        c_achterland=inputs["c_3"],
        polderpeil=inputs["pp"],
        buitenwaterstand=inputs["h"],
        L_intrede=inputs["DIST_L_GEOM"],
        L_but=inputs["DIST_BUT"],
        L_bit=inputs["DIST_BIT"],
        mv_exit=inputs["mv"],
        top_zand=inputs["top_zand"],
        kD_wvp=inputs["kD_WVP"],
        modelfactor_u=inputs["mu"],
        gamma_water=inputs["gamma_w"],
        gamma_sat_deklaag=inputs["gamma_sat_cover"],
        D_wvp=inputs["D_zand"],
    )
    assert result[0] == pytest.approx(expected["Z_u"], 0.01)
    assert result[1] == pytest.approx(expected["L1"], 0.01)
    assert result[2] == pytest.approx(expected["r"], 0.01)
    assert result[3] == pytest.approx(expected["pot_exit"], 0.01)
    assert result[4] == pytest.approx(expected["h_exit"], 0.01)
    assert result[5] == pytest.approx(expected["Dcover"], 0.01)
    assert result[6] == pytest.approx(expected["d_pot_cu"], 0.01)
