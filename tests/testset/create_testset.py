"""Create a test set for piping calculations."""

import itertools

import numpy as np
import pandas as pd


def create_permutations_dataframe(**kwargs):
    """
    Create a DataFrame with all possible permutations of the provided variables.

    Parameters:
        **kwargs: Each keyword argument represents a variable name and its list of possible values.

    Returns:
        pd.DataFrame: A DataFrame containing all permutations of the input variables.
    """
    # Extract variable names and their values
    variable_names = kwargs.keys()
    variable_values = kwargs.values()

    # Generate all possible permutations
    permutations = list(itertools.product(*variable_values))

    # Create a DataFrame from the permutations
    df = pd.DataFrame(permutations, columns=list(variable_names))

    return df


# Example usage
# variables = {
#     "dist_L_geom": [200.0, 500.0, 1000.0],
#     "distBUT": [20.0, 40.0],
#     "gamma_w": [9.81],
#     "h": [0.0, 5.0, 10.0],
# }

# list_of_variables = [
#     dist_L_geom,
#     dist_BUT,
#     dist_BIT,
#     L3_geom,
#     mv,
#     pp,
#     top_zand,
#     gamma_sat_cover,
#     gamma_w,
#     kD,
#     D,
#     d70,
#     c_1,
#     c_3,
#     mu,
#     mh,
#     mp,
#     i_c_h,
#     rc,
#     h,
# ]

size = 5

variables = {
    "dist_L_geom": [10.0, 100.0, 500.0],
    "distBUT": [20.0],
    "distBIT": [5.0],
    "L3_geom": [500.0, 3000.0],
    "mv": [0.0],
    "pp": [0.0],
    "top_zand": np.linspace(-10.0, 0.1, size),
    "gamma_sat_cover": [15.0],
    "gamma_w": [9.81],
    "k": np.linspace(1.0, 120.0, size),
    "D": np.linspace(1.5, 60.0, size),
    "d70": np.linspace(1.5e-4, 5.0e-4, size),
    "c_1": np.linspace(1, 100.0, size),
    "c_3": np.linspace(1, 600.0, size),
    "mu": [1.0],
    "mh": [1.0],
    "mp": [1.0],
    "i_c_h": [0.3],
    "rc": [0.3],
    "h": np.linspace(0.0, 10.0, size),
}

df = create_permutations_dataframe(**variables)
df["kD"] = df["k"] * df["D"]
df.to_excel("tests/testset/input_testset.xlsx", index=False)
