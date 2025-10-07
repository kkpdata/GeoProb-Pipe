import pytest
from . import piping


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
input_keys_calc_z_piping = [
    "c_1", # c_voorland
    "h", # buitenwaterstand
    "pp", # polderpeil
    "mv", # mv_exit
    "DIST_BUT", # L_but
    "DIST_L_GEOM", # L_intrede
    "mp", # modelfactor_h
    "D70", # d70
    "D_zand", # D_wvp
    "kD_WVP", # kD_wvp
    "top_zand", # top_zand
    # GAMMA_WATER not in excel file, use global variable
    # G not in excel file, use global variable
    # V not in excel file, use global variable
    # THETA not in excel file, use global variable
    # ETA not in excel file, use global variable
    # D70_M not in excel file, use global variable
    # GAMMA_KORREL not in excel file, use global variable
    "rc" # r_c_deklaag
    ]

output_key_calc_z_piping = [
    "Z_p", # z_p
    "L1", # lengte_voorland
    "Lambda_1", # lambda_voorland
    "W_1", # W_voorland
    "L_kwelweg", # L_kwelweg
    "dHc_piping", # dh_c
    "h_exit", # h_exit
    "Dcover", # d_deklaag  
    "dhred", # dh_red
    ] 

# global variables
G = 9.81  # m/s^2
V = 1.33e-6  # m^2/s
ETA = 0.25  # [-]
THETA = 37.0  # grd
GAMMA_KORREL = 26.0  # kN/m^3
GAMMA_WATER = 9.81  # kN/m^3
D70_M = 2.08e-4  # m

#setup test construct
data_calc_z_piping = get_data()
inputs_calc_z_piping = data_calc_z_piping.loc[:,input_keys_calc_z_piping]
#add global variables in dataframe in the right order
inputs_calc_z_piping["g"] = G
inputs_calc_z_piping["v"] = V
inputs_calc_z_piping["eta"] = ETA
inputs_calc_z_piping["theta"] = THETA
inputs_calc_z_piping["gamma_korrel"] = GAMMA_KORREL
inputs_calc_z_piping["gamma_water"] = GAMMA_WATER
inputs_calc_z_piping["d70_m"] = D70_M
#reorder columns
input_keys_right_order = [
    "c_1", # c_voorland
    "h", # buitenwaterstand
    "pp", # polderpeil
    "mv", # mv_exit
    "DIST_BUT", # L_but
    "DIST_L_GEOM", # L_intrede
    "mp", # modelfactor_h
    "D70", # d70
    "D_zand", # D_wvp
    "kD_WVP", # kD_wvp
    "top_zand", # top_zand
    "gamma_water",
    "g",
    "v",
    "theta",
    "eta",
    "d70_m",
    "gamma_korrel",
    "rc" # r_c_deklaag
]
inputs_calc_z_piping_dict = inputs_calc_z_piping.to_dict(orient="records")
expected_outputs_calc_z_piping = data_calc_z_piping[output_key_calc_z_piping].to_dict(orient="records")

@pytest.mark.parametrize("inputs, expected", zip(inputs_calc_z_piping_dict, expected_outputs_calc_z_piping))
def test_calc_z_piping(inputs, expected):
    """Test calc_dh_c function with multiple test cases from excel file"""
    result = piping.z_piping(
        c_voorland=inputs["c_1"],
        buitenwaterstand=inputs["h"],
        polderpeil=inputs["pp"],
        mv_exit=inputs["mv"],
        L_but=inputs["DIST_BUT"],
        L_intrede=inputs["DIST_L_GEOM"],
        modelfactor_p=inputs["mp"],
        d70=inputs["D70"],
        D_wvp=inputs["D_zand"],
        kD_wvp=inputs["kD_WVP"],
        top_zand=inputs["top_zand"],
        gamma_water=inputs["gamma_water"],
        g=inputs["g"],
        v=inputs["v"],
        theta=inputs["theta"],
        eta=inputs["eta"],
        d70_m=inputs["d70_m"],
        gamma_korrel=inputs["gamma_korrel"],
        r_c_deklaag=inputs["rc"]
    )
    assert result[0] == pytest.approx(expected["Z_p"], 0.01)
    assert result[1] == pytest.approx(expected["L1"], 0.01)
    assert result[2] == pytest.approx(expected["Lambda_1"], 0.01)
    assert result[3] == pytest.approx(expected["W_1"], 0.01)
    assert result[4] == pytest.approx(expected["L_kwelweg"], 0.01)
    assert result[5] == pytest.approx(expected["dHc_piping"], 0.01)
    assert result[6] == pytest.approx(expected["h_exit"], 0.01)
    assert result[7] == pytest.approx(expected["Dcover"], 0.01)
    assert result[8] == pytest.approx(expected["dhred"], 0.01)
