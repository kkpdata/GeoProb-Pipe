from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables, \
    _construct_df_identifiers, _combine_parameter_invoer_sources, _add_fragility_values_to_combined_parameter_invoer, \
    _collect_right_columns_combined_parameter_invoer, _expand, _concat_collection
from typing import Dict, List
from pandas import DataFrame, isna, notna, concat, read_sql
import sqlite3
import numpy as np
from geopandas import GeoDataFrame, read_file
from geoprob_pipe.calculations.system_calculations.dummy_input_mapper import DUMMY_INPUT_MAPPER
from geoprob_pipe.questionnaire.parameter_input.input_parameter_tables import InputParameterTables
from probabilistic_library import FragilityValue


path_to_geopackage = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\tests\systeem_testen\224\Traject224_model4a_WBN_prob.geoprob_pipe.gpkg"
df_expanded = run_expand_input_tables(geopackage_filepath=path_to_geopackage, add_frag_ref=True)

# df = df_expanded
#
# ##
# df = df[df["parameter_name"] == "buitenwaterstand"]
#
# ##
#
# from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables, \
#     _construct_df_identifiers, _combine_parameter_invoer_sources, _add_fragility_values_to_combined_parameter_invoer, \
#     _collect_right_columns_combined_parameter_invoer, _expand, _concat_collection
# from typing import Dict, List
# from pandas import DataFrame, isna, notna, concat, read_sql
# import sqlite3
# import numpy as np
# from geopandas import GeoDataFrame, read_file
# from geoprob_pipe.calculations.system_calculations.dummy_input_mapper import DUMMY_INPUT_MAPPER
# from geoprob_pipe.questionnaire.parameter_input.input_parameter_tables import InputParameterTables
# from probabilistic_library import FragilityValue
#
#
# geopackage_filepath = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\tests\systeem_testen\224\Traject224_model4a_WBN_prob.geoprob_pipe.gpkg"
# # df_expanded = run_expand_input_tables(geopackage_filepath=geopackage_filepath)
#
# tables = InputParameterTables(geopackage_filepath=geopackage_filepath)
# df_identifiers = _construct_df_identifiers(geopackage_filepath=geopackage_filepath, tables=tables)
#
# # Construct df_parameter_invoer_combined
# df_parameter_invoer_combined1 = _combine_parameter_invoer_sources(tables=tables)
#
# df_parameter_invoer_combined2 = _add_fragility_values_to_combined_parameter_invoer(
#     df_parameter_invoer_combined=df_parameter_invoer_combined1, tables=tables,
#     geopackage_filepath=geopackage_filepath, drop_ref=False)
# df_parameter_invoer_combined3 = _collect_right_columns_combined_parameter_invoer(
#     df_parameter_invoer_combined=df_parameter_invoer_combined2)
#
# # Expand
# collection: Dict[str, DataFrame] = _expand(
#     df_parameter_invoer_combined=df_parameter_invoer_combined3,
#     df_identifiers=df_identifiers,
#     geopackage_filepath=geopackage_filepath)
#
# df_expanded = _concat_collection(collection=collection)
#
# # df_expanded.to_excel(f"df_expanded.xlsx")
#
# ##

df = df_expanded
df = df[df["parameter_name"] == "buitenwaterstand"]
print(df['parameter_input'].iloc[0])



from pandas import Series, concat
expanded = df['parameter_input'].apply(Series)
df = concat([df.drop(columns=['parameter_input']), expanded], axis=1)


used_frag_refs = df['fragility_values_ref'].unique()


##

# df_result = (
#     df.groupby('fragility_values_ref')['uittredepunt_id']
#       .apply(lambda x: ', '.join(map(str, x)))
#       .reset_index(name='uittredepunt_ids'))

df_result = (
    df.groupby('fragility_values_ref').agg({
        'uittredepunt_id': lambda x: ', '.join(map(str, x)),  # concatenate IDs
        'fragility_values': 'first'  # keep the first list (since all are equal per ref)
    }).reset_index())
df_result = df_result.rename(columns={"uittredepunt_id": "uittredepunt_ids"})

##

df_result['uittredepunt_ids_multiline'] = ""
for index, row in df_result.iterrows():
    arr = row['uittredepunt_ids'].split(", ")
    lines = [' '.join(arr[i:i+5]) for i in range(0, len(arr), 5)]
    df_result.loc[index, 'uittredepunt_ids_multiline'] = '\n'.join(lines)


##

from pandas import DataFrame
df_unique_combos: DataFrame = df_expanded[["uittredepunt_id", "ondergrondscenario_naam"]].drop_duplicates()

for index, row in df_unique_combos.iterrows():
    df_filter = df_expanded[
        (df_expanded["uittredepunt_id"] == row["uittredepunt_id"]) &
        (df_expanded["ondergrondscenario_naam"] == row["ondergrondscenario_naam"])
    ]
    break



##

from geoprob_pipe.calculations.system_calculations.piping_moria.reliability_calculation import  (
    PipingMORIASystemReliabilityCalculation)


df = df_filter.copy(deep=True)


# For now change buitenwaterstand  # TODO
# new_dict = {'distribution_type': 'deterministic', 'mean': 6.0, 'name': 'buitenwaterstand'}
# df.loc[df['parameter_name'] == 'buitenwaterstand', 'parameter_input'] = [new_dict] * df[df['parameter_name'] == 'buitenwaterstand'].shape[0]

df['parameter_input'] = df.apply(
    lambda row: {**row['parameter_input'], 'name': row['parameter_name']},
    axis=1
)
calculation_input = df['parameter_input'].values.tolist()

obj = PipingMORIASystemReliabilityCalculation(system_variable_distributions=calculation_input)


# from geopandas import GeoDataFrame, read_file
# from geoprob_pipe.utils.validation_messages import BColors
# from pathlib import Path
# import fiona
# import sqlite3
# from pandas import read_sql_query
# from pandas import DataFrame
#
# ##
#
#
#
#
# ##
#
# geopackage_filepath = r"C:\Users\CP\Downloads\C_Analyse_corr\16-1\Analyse_16-1_test_gisjointable.geoprob_pipe.gpkg"
#
# # Getting necessary GeoDataframes
# gdf_exit_points: GeoDataFrame = read_file(geopackage_filepath, layer="uittredepunten")
# # gdf_polderpeil: GeoDataFrame = read_file(geopackage_filepath, layer="polderpeil")
#
# # Check if already added
# # if "polderpeil" in gdf_exit_points.columns:
# #     print(BColors.OKBLUE, f"✔  Polderpeil al gekoppeld aan uittredepunten.", BColors.ENDC)
# #     return True  # Assuming already added
# # TODO
# # if "polderpeil" in gdf_exit_points.columns:
# #     gdf_exit_points = gdf_exit_points.drop(columns=["polderpeil"])
#
#
# # Perform spatial join to find the nearest HRD-location for each Exit Point
# # gdf_exit_with_hrd = gdf_exit_points.sjoin_nearest(
# #     gdf_polderpeil[['geometry', 'polderpeil']], how='left', distance_col='distance')
#
#
# from pandas import DataFrame
# import numpy as np
#
# columns_to_keep = ["uittredepunt_id", "afstand_intredelijn"]
#
# df: DataFrame = gdf_exit_points[columns_to_keep]
# df = df.rename(columns={"afstand_intredelijn": "mean"})
#




##

##

# # Define which columns to keep (after spatial join)
# columns_to_keep = list(gdf_exit_points.columns)
# columns_to_keep.append("polderpeil")
# gdf_new_exit_points = gdf_exit_with_hrd[columns_to_keep]
#
# # Store back in geopackage
# gdf_new_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
# print(BColors.OKBLUE, f"✅  Polderpeil is nu gekoppeld aan de uittredepunten.", BColors.ENDC)
# return True
#



# from geopandas import GeoDataFrame, read_file
#
#
#
#
# # Convert to dictionary with 'id' as keys
# gdf_uittredepunten: GeoDataFrame = read_file(
#     r"C:\Users\CP\Downloads\C_Analyse_corr\Nieuwe map (12)\Analyse224.geoprob_pipe.gpkg", layer="uittredepunten")
# gdf_dict = gdf_uittredepunten.set_index('uittredepunt_id').to_dict(orient='index')
#
#
#
# ##
#
# import fiona
# from geopandas import read_file, GeoDataFrame
#
# layers = fiona.listlayers(r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\DT16-1_STPH.gpkg")
#
# gdf: GeoDataFrame = read_file(
#     r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\DT16-1_STPH.gpkg",
#     layer="VakindelingGEOTECH_16_1_table")
# gdf = gdf.sort_values(by=["M_VAN"])
# # gdf.to_excel("vakindeling_16-1.xlsx")
#
#
# ## Exit point Excel to GDF
#
# from pandas import read_excel
#
# path_to_excel = r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\3_Resultaat_scenarioberekeningen_LBO1.xlsx"
# df_resultaten_lbo1 = read_excel(path_to_excel)
#
#
# from geopandas import GeoDataFrame, points_from_xy
#
# gdf_resultaten_lbo1 = GeoDataFrame(
#     df_resultaten_lbo1,
#     geometry=points_from_xy(df_resultaten_lbo1['X_uittrede'], df_resultaten_lbo1['Y_uittrede']),
#     crs='EPSG:28992')
# gdf_resultaten_lbo1 = gdf_resultaten_lbo1.drop(columns=["VakID", "Vaknaam_x"])
#
# ## Import vakindeling
# from geopandas import read_file, GeoDataFrame
# import fiona
#
# layers = fiona.listlayers(r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\DT16-1_STPH.gpkg")
# gdf_vakindeling: GeoDataFrame = read_file(
#     r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\DT16-1_STPH.gpkg",
#     layer="VakindelingGEOTECH_16_1")
# gdf_vakindeling = gdf_vakindeling.sort_values(by=["M_VAN"])
# gdf_vakindeling = gdf_vakindeling.rename(columns={"Q__count": "vak_id", "Vaknaam": "vak_naam"})
#
# ## Spatial join vakindeling
#
# gdf_exit_points_with_vakken = gdf_resultaten_lbo1.sjoin_nearest(
#     gdf_vakindeling[['geometry', 'vak_id', 'vak_naam']], how='left', distance_col='distance_to_vak')
# gdf_exit_points_with_vakken.to_excel(r"K:\DATATOETSING\Werkmap\DT16-1_STPH\workspace\input\uittredepunten_sjoin_vakken.xlsx")
#
#
#
# from geopandas import GeoDataFrame, read_file
# gdf_vakindeling: GeoDataFrame = read_file(
#     r"C:\Users\CP\Downloads\C_Analyse_corr\Nieuwe map (12)\Analyse224.geoprob_pipe.gpkg", layer="vakindeling")
#
# gdf_vakindeling['id'] = gdf_vakindeling['id'] + 3
#
# from pathlib import Path
# gdf_vakindeling.to_file(Path(r"C:\Users\CP\Downloads\C_Analyse_corr\Nieuwe map (13)\vakindeling.shp"))
