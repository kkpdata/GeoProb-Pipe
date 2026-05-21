

def test_class_traject_normering():
    ##

    from geoprob_pipe.input_data.traject_normering import TrajectNormering
    from repo_utils.utils import repository_root_path
    import os
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    # filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg")
    filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "Traject224_v2.2.3.geoprob_pipe.gpkg")
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)

    _ = TrajectNormering(app_settings=app_settings)

    ##