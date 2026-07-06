
def test_system():

    ##

    from repo_utils.utils import repository_root_path
    from geoprob_pipe import GeoProbPipe
    import os
    repo_root = repository_root_path()
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

    file_names = ["unit_testset_dt224.geoprob_pipe.gpkg"]

    for file_name in file_names:
        print(f"\nNow running {file_name}")
        app_settings = ApplicationSettings()
        filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", file_name)
        app_settings.workspace_dir = os.path.dirname(filepath)
        app_settings.geopackage_filename = os.path.basename(filepath)
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()

    ##
