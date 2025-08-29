

def test_pre_processing():

    ##

    from geoprob_pipe.pre_processing.questionnaire import pre_processing_questionnaire
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
    from repo_utils.utils import repository_root_path
    import os

    # Create application settings
    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    app_settings.workspace_dir = os.path.join(repo_root, "geoprob_pipe", "pre_processing", "test_files")
    app_settings.geopackage_filename = os.path.basename("Analyse224.geoprob_pipe.gpkg")

    # Perform test
    pre_processing_questionnaire(app_settings=app_settings)

    ##
