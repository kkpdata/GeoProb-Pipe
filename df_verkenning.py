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
