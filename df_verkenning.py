from geopandas import GeoDataFrame, read_file




# Convert to dictionary with 'id' as keys
gdf_vakindeling: GeoDataFrame = read_file(
    r"C:\Users\CP\Downloads\C_Analyse_corr\Nieuwe map (12)\Analyse224.geoprob_pipe.gpkg", layer="uittredepunten")
# gdf_dict = gdf_vakindeling.set_index('fid').to_dict(orient='index')
