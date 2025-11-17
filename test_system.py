from charset_normalizer.md import ArchaicUpperLowerPlugin


def test_system():

    ##

    from repo_utils.utils import repository_root_path
    from geoprob_pipe import GeoProbPipe
    import os
    repo_root = repository_root_path()
    workspace_path = os.path.join(repo_root, "workspaces", "traject_224")
    geoprob_pipe = GeoProbPipe(workspace_path)
    geoprob_pipe.export_archive()

    ##


def test_system_moria():

    ##

    from repo_utils.utils import repository_root_path
    from geoprob_pipe import GeoProbPipe
    import os
    repo_root = repository_root_path()
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
    app_settings = ApplicationSettings()

    filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "Traject224_MORIA.geoprob_pipe.gpkg")
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)

    geoprob_pipe = GeoProbPipe(app_settings)
    geoprob_pipe.export_archive()

    ##


def test_system_moria_deest_bovenleeuwen():

    ##

    from geoprob_pipe import GeoProbPipe
    import os
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
    app_settings = ApplicationSettings()

    filepath = r"C:\Users\CP\Downloads\Deest_BovenLeeuwen\Deest_BovenLeeuwen_Test.geoprob_pipe.gpkg"
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)

    geoprob_pipe = GeoProbPipe(app_settings)
    geoprob_pipe.export_archive()

    ##
