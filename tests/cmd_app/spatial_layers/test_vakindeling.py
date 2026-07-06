

def test_vakindeling():

    ##

    import geoprob_pipe.cmd_app.spatial_layers.vakindeling as vakindeling_cmd
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

    # Perform test step03 (not loaded yet)
    app_settings = ApplicationSettings()
    app_settings.workspace_dir = os.path.dirname(filepath_test)
    app_settings.geopackage_filename = os.path.basename(filepath_test)
    vakindeling_cmd.validate_vakindeling(gdf=gdf_vakindeling)
    vakindeling_cmd.align_vak_shp_to_dijktraject(
        app_settings=app_settings, gdf_vakindeling=gdf_vakindeling, kolom_vak_naam="naam", kolom_vak_id="id")

    # Remove test file
    os.remove(filepath_test)

    ##

    # List columns (correct, but for process returns also False)
    assert vakindeling_cmd.validity_column_vak_id(column_name="listcolumns", gdf=gdf_vakindeling) is False

    # Non-existent column
    assert vakindeling_cmd.validity_column_vak_id(column_name="non_existent", gdf=gdf_vakindeling) is False

    # Not unique
    gdf_vakindeling['non_unique'] = "non_unique_value"
    assert vakindeling_cmd.validity_column_vak_id(column_name="non_unique", gdf=gdf_vakindeling) is False

    # Not integers
    assert vakindeling_cmd.validity_column_vak_id(column_name="naam", gdf=gdf_vakindeling) is False


    assert vakindeling_cmd.validity_column_vak_id(column_name="non_unique", gdf=gdf_vakindeling) is False

    ##

    # Perform test step03 (already loaded)
    app_settings = ApplicationSettings()
    app_settings.workspace_dir = os.path.dirname(filepath_data)
    app_settings.geopackage_filename = os.path.basename(filepath_data)

    # Perform test
    vakindeling_cmd.check_validity_vakindeling(app_settings=app_settings)

    ##