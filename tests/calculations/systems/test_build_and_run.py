

def test_worker():
    ##
    from geoprob_pipe.calculations.systems.build_and_run import _worker, _init_worker
    from repo_utils.utils import repository_root_path
    import os
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg")
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)
    model = app_settings.geohydrologisch_model
    _init_worker(
        geohydrologisch_model=model,
        geopackage_filepath=filepath,
        to_run_vakken_ids=None)
    result = _worker(row_unique={'uittredepunt_id': 1, 'ondergrondscenario_naam': 'scenario1', 'vak_id': 4})

    ##