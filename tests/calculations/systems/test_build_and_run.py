

def test_worker():
    ##
    from geoprob_pipe.calculations.systems.build_and_run import _worker, _init_worker
    from repo_utils.utils import repository_root_path
    import os
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "unit_testset_dt224.geoprob_pipe.gpkg")
    assert os.path.exists(filepath)
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)
    model = app_settings.geohydrologisch_model
    _init_worker(
        geohydrologisch_model=model,
        geopackage_filepath=filepath,
        to_run_vakken_ids=None)
    _ = _worker(row_unique={'uittredepunt_id': 1, 'ondergrondscenario_naam': 'scenario1', 'vak_id': 4})

    ##


def test_collect_df_and_worker():

    ##

    from geoprob_pipe import SystemCalculation
    from geoprob_pipe.results.construct_dataframes import collect_df_beta_scenario_final
    from geoprob_pipe.calculations.systems.mappers.calculations import CALCULATION_MAPPER
    import os
    from repo_utils.utils import repository_root_path
    from geoprob_pipe.calculations.systems.build_and_run import _worker

    repo_root = repository_root_path()
    geopackage_filepath: str = os.path.join(
        repo_root, "tests", "systeem_testen", "224", "unit_testset_dt224.geoprob_pipe.gpkg")
    builder = CALCULATION_MAPPER["model4a"]["system_builder"](
        geopackage_filepath=geopackage_filepath, to_run_vakken_ids=None)
    row_unique = {'uittredepunt_id': 1, 'ondergrondscenario_naam': 'PL', 'vak_id': 0}
    calc: SystemCalculation = builder.build_instance(row_unique=row_unique)
    calc.run()
    _ = collect_df_beta_scenario_final(calc)

    # Worker
    _ = _worker(row_unique)

    ##


def test_build_and_run_system_calculations():
    ##

    from geoprob_pipe import GeoProbPipe
    from repo_utils.utils import repository_root_path
    import os
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

    app_settings = ApplicationSettings()
    repo_root = repository_root_path()
    filepath = os.path.join(repo_root, "tests", "systeem_testen", "224", "unit_testset_dt224.geoprob_pipe.gpkg")
    assert os.path.exists(filepath)
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)
    app_settings.to_run = "vakken:4,5"
    _ = GeoProbPipe(app_settings)

    ##
