

def test_vakindeling():

    ##

    from geoprob_pipe.cmd_app.spatial_layers.vakindeling import align_vak_shp_to_dijktraject
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings
    from geopandas import GeoDataFrame, read_file
    from repo_utils.utils import repository_root_path
    import os
    import shutil

    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    filepath = os.path.join(
        repo_root, "tests", "systeem_testen", "224", "input_steps", "step04_load_hrd.geoprob_pipe.gpkg")
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)
    root_dir: str = os.path.join(repo_root, "tests", "systeem_testen", "224", "input_steps")

    # Template file
    filepath = os.path.join(root_dir, "step03_load_vakindeling.geoprob_pipe.gpkg")
    filepath_test = os.path.join(root_dir, "test.geoprob_pipe.gpkg")
    shutil.copy2(src=filepath, dst=filepath_test)

    # Load test data
    filepath_data = os.path.join(root_dir, "step04_load_hrd.geoprob_pipe.gpkg")
    gdf_vakindeling: GeoDataFrame = read_file(filepath_data, layer="vakindeling")

    # Perform test
    app_settings = ApplicationSettings()
    app_settings.workspace_dir = os.path.dirname(filepath_test)
    app_settings.geopackage_filename = os.path.basename(filepath_test)
    align_vak_shp_to_dijktraject(
        app_settings=app_settings, gdf_vakindeling=gdf_vakindeling, kolom_vak_naam="naam", kolom_vak_id="id")

    # Remove test file
    os.remove(filepath_test)

    ##
