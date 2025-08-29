""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
from repo_utils.utils import repository_root_path
from geoprob_pipe import GeoProbPipe
from dotenv import load_dotenv
import os


# Import environment variables
repo_root = repository_root_path()
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))


# Initiate GeoProb-Pipe project object
geoprob_pipe = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
geoprob_pipe.export_archive()


##
#
# from probabilistic_library import Alpha, Stochast
# from geoprob_pipe.calculations.limit_states.piping import z_piping
# from geoprob_pipe.calculations.limit_states.uplift_icw_model4a import z_uplift
# from geoprob_pipe.calculations.limit_states.heave_icw_model4a import z_heave
#
# # kwargs = {alpha.variable: alpha.x for alpha in project.calculations[0].system_design_point.alphas}
# # kwargs = {alpha.variable: alpha.x for alpha in system_calculation.alphas}
#
#
# # Get kwargs per calculation
# df = geoprob_pipe.results.df_beta_scenarios.copy(deep=True)
# df['physical_values'] = df['system_calculation'].apply(
#     lambda sc: {alpha.variable.name: alpha.x for alpha in sc.system_design_point.alphas}
# )
#
#
# # Calculate the derived values
# # Calculate the derived values
# def derived_values_single_calculation(**kwargs):
#     heave_return_keys = ["z_h", "lengte_voorland", "r_exit", "phi_exit", "h_exit", "d_deklaag", "i_exit"]
#     heave_derived_values = {key: value for key, value in zip(heave_return_keys, z_heave(**kwargs))}
#
#     uplift_return_keys = ["z_u", "L_voorland", "r_exit", "phi_exit", "h_exit", "d_deklaag", "dphi_c_u"]
#     uplift_derived_values = {key: value for key, value in zip(uplift_return_keys, z_uplift(**kwargs))}
#
#     piping_return_keys = [
#         "z_p", "L_voorland", "lambda_voorland", "W_voorland", "L_kwelweg", "dh_c", "h_exit", "d_deklaag", "dh_red"]
#     piping_derived_values = {key: value for key, value in zip(piping_return_keys, z_piping(**kwargs))}
#
#     return {
#         **heave_derived_values,
#         **uplift_derived_values,
#         **piping_derived_values,
#     }
#
# df['derived_physical_values'] = df['physical_values'].apply(
#     lambda kwargs: derived_values_single_calculation(**kwargs)
# )
#
#
# ##
# import numpy as np
# df_new = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id", "derived_physical_values"]].copy(deep=True)
# df_new['design_point'] = "system"
# df_new['distribution_type'] = "derived"
# df_new['alpha'] = np.nan
# df_new['influence_factor'] = np.nan

##

# derived_values = df.iloc[0]['derived_physical_values']


##

# kwargs = df.iloc[0]['physical_values']
# # derived_values = derived_values_single_calculation(**kwargs)
# heave_return_keys = ["z_h", "lengte_voorland", "r_exit", "phi_exit", "h_exit", "d_deklaag", "i_exit"]
# heave_derived_values = {key: value for key, value in zip(heave_return_keys, z_heave(**kwargs))}


##
#
# df['derived_physical_values'] = df['physical_values'].apply(
#     lambda kwargs: derived_values_single_calculation(**kwargs)
# )


##


# import pandas as pd

# Example DataFrame
# df = pd.DataFrame({
#     'col1': ['A', 'B'],
#     'col2': [1, 2],
#     'col3': ['X', 'Y'],
#     'col4': ['North', 'South'],
#     'col5': ['Active', 'Inactive'],
#     'dict_col': [
#         {'length': 10, 'width': 5},
#         {'length': 20, 'height': 15}
#     ]
# })

# # Convert each row into multiple rows based on the dictionary
# expanded_df = pd.concat([
#     pd.DataFrame({
#         **row.drop('derived_physical_values'),
#         'variable': list(row['derived_physical_values'].keys()),
#         'physical_value': list(row['derived_physical_values'].values())
#     })
#     for _, row in df_new.iterrows()
# ], ignore_index=True)
#
# print(expanded_df)
# expanded_df.to_excel("expanded_df.xlsx")


##

# from geoprob_pipe.results.df_alphas_influence_factors_and_physical_values import construct_df
#
# df_new_pv = construct_df(geoprob_pipe=geoprob_pipe)
