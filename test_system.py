from charset_normalizer.md import ArchaicUpperLowerPlugin


# def test_system():
#
#     ##
#
#     from repo_utils.utils import repository_root_path
#     from geoprob_pipe import GeoProbPipe
#     import os
#     repo_root = repository_root_path()
#     workspace_path = os.path.join(repo_root, "workspaces", "traject_224")
#     geoprob_pipe = GeoProbPipe(workspace_path)
#     geoprob_pipe.export_archive()
#
#     ##


def test_system():

    ##

    from repo_utils.utils import repository_root_path
    from geoprob_pipe import GeoProbPipe
    import os
    repo_root = repository_root_path()
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings

    file_names = [
        "Traject224_MORIA_WBN_det.geoprob_pipe.gpkg",
        "Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg",
        "Traject224_model4a_WBN_prob.geoprob_pipe.gpkg",
        # "Traject224_WBI_WBN_prob.geoprob_pipe.gpkg",  # TODO
    ]

    for file_name in file_names:
        print(f"Now running {file_name}\n")
        app_settings = ApplicationSettings()
        filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", file_name)
        app_settings.workspace_dir = os.path.dirname(filepath)
        app_settings.geopackage_filename = os.path.basename(filepath)
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()

    ##
