

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

    from pandas import DataFrame
    import numpy as np
    from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import PIPING_DUMMY_INPUT

    # Construct base dataframe
    df_dummy_data = DataFrame(PIPING_DUMMY_INPUT)  # TODO: Geohydrologische model keuze moet nog opgehaald worden
    df_dummy_data = df_dummy_data.sort_values(by=["name"])
    df_parameter_invoer = df_dummy_data[["name", "distribution_type", "mean", "variation", "deviation"]].copy()

    # Add missing columns
    df_parameter_invoer.loc[:, "minimum"] = np.nan
    df_parameter_invoer.loc[:, "maximum"] = np.nan
    df_parameter_invoer.loc[:, "scope"] = "traject"
    df_parameter_invoer.loc[:, "scope_referentie"] = ""
    df_parameter_invoer.loc[:, "ondergrondscenario_naam"] = ""

    # Sort columns
    df_parameter_invoer = df_parameter_invoer[[
        "name", "scope", "scope_referentie", "ondergrondscenario_naam",
        "distribution_type", "mean", "variation", "deviation", "minimum", "maximum", "fragility_values"]].copy()

    ## Validation if parameter invoer columns are complete (e.g. variation is available if lognormal)
    # TODO

    # ## Collect fragility values
    # # TODO
    #
    # # Gather referenced fragility value refs
    # from pandas import DataFrame, read_excel, notna, isna
    # path_to_excel = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\geoprob_pipe\pre_processing\parameter_input\input_voorstel_v4.xlsx"
    # df_parameter_invoer: DataFrame = read_excel(path_to_excel, sheet_name="Parameter invoer", header=3)
    # fragility_refs = df_parameter_invoer['fragility_values_ref'].dropna().unique()
    #
    # # Collect fragility lines
    # df_frag_lines = DataFrame(
    #     data={"fragility_values_ref": fragility_refs, "fragility_values": ["TODO"] * fragility_refs.__len__()})
    # # TODO: Collecting should still be done. This is just a temporary value of 'TODO'
    #
    # # Attach to parameter invoer df
    # df_parameter_invoer = df_parameter_invoer.merge(
    #     df_frag_lines, left_on="fragility_values_ref", right_on="fragility_values_ref", how="left")
    # df_parameter_invoer = df_parameter_invoer.drop(columns=["fragility_values_ref"])


    # ## Parameter tabel omzetten naar juiste kolom onderdelen
    #
    # # Add parameter invoer: op uittredepunten niveau
    # df_parameter_invoer = df_parameter_invoer.drop(columns=["bronnen", "opmerking"])
    # parameter_description_columns = [
    #     "distribution_type", "mean", "variation", "deviation", "minimum", "maximum", "fragility_values"]
    # df_parameter_invoer['parameter_input'] = df_parameter_invoer.apply(lambda row: {
    #     k: row[k] for k in parameter_description_columns if notna(row[k])
    # }, axis=1)
    # df_parameter_invoer = df_parameter_invoer.drop(columns=parameter_description_columns)


    ## Create identifiers table (base for exploding to input per scenario and uittredepunt)

    # df_identifiers = geoprob_pipe.input_data.uittredepunten.df[["uittredepunt_id", "vak_id"]]
    # df_scenario_invoer: DataFrame = read_excel(path_to_excel, sheet_name="Scenario invoer", header=2)
    # df_identifiers = df_identifiers.merge(df_scenario_invoer, left_on="vak_id", right_on="vak_id")
    # df_identifiers = df_identifiers.drop(columns=["kans"])


    ## Gather required input arguments

    # from geoprob_pipe.calculations.system_calculations.piping_moria.reliability_calculation import \
    #     PipingMORIASystemReliabilityCalculation
    # from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import PIPING_DUMMY_INPUT
    # import inspect
    #
    # reliability_calculation = PipingMORIASystemReliabilityCalculation(PIPING_DUMMY_INPUT)
    # sig = inspect.signature(reliability_calculation.given_system_variables_setup_function)
    # required_args = [
    #     name for name, param in sig.parameters.items()
    #     if param.default == inspect.Parameter.empty and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
    # ]  # TODO: Use in iteration to retrieve data


    ## Copied to file

    # # Add parameter invoer: op uittredepunten niveau
    # parameter_names = ["mv_exit", "gamma_sat_deklaag"]
    # collection_of_dfs = {}
    # for parameter_name in parameter_names:
    #
    #     # Gather and merge input on uittredepunten-niveau
    #     df_gather = df_parameter_invoer[
    #         (df_parameter_invoer['parameter'] == parameter_name) &
    #         (df_parameter_invoer['scope'] == 'uittredepunt')]
    #     df_gather = df_gather[["scope_referentie", "parameter_input"]]
    #     df = df_identifiers.copy(deep=True).merge(
    #         df_gather, how="left", left_on="uittredepunt_id", right_on="scope_referentie")
    #     df = df.drop(columns=["scope_referentie"])
    #
    #     # Vak / scenario niveau
    #     df_gather = df_parameter_invoer[
    #         (df_parameter_invoer['parameter'] == parameter_name) &
    #         (df_parameter_invoer['scope'] == 'vak') &
    #         (df_parameter_invoer['ondergrondscenario_naam'].notna())]
    #     df_gather = df_gather[["scope_referentie", "ondergrondscenario_naam", "parameter_input"]]
    #     df_gather = df_gather.rename(columns={
    #         "scope_referentie": "vak_id",
    #         "ondergrondscenario_naam": "naam"})
    #     df['parameter_input'] = df['parameter_input'].combine_first(
    #         df_identifiers.copy(deep=True).merge(df_gather, on=["vak_id", "naam"], how="left")['parameter_input'])
    #
    #     # Vak niveau
    #     df_gather = df_parameter_invoer[
    #         (df_parameter_invoer['parameter'] == parameter_name) &
    #         (df_parameter_invoer['scope'] == 'vak') &
    #         (df_parameter_invoer['ondergrondscenario_naam'].isna())]
    #     df_gather = df_gather[["scope_referentie", "parameter_input"]]
    #     df_gather = df_gather.rename(columns={"scope_referentie": "vak_id"})
    #     df['parameter_input'] = df['parameter_input'].combine_first(
    #         df_identifiers.copy(deep=True).merge(df_gather, on=["vak_id"], how="left")['parameter_input'])
    #
    #     # Traject niveau
    #     df_gather = df_parameter_invoer[
    #         (df_parameter_invoer['parameter'] == parameter_name) &
    #         (df_parameter_invoer['scope'] == 'traject')]
    #     if df_gather.__len__() >= 1:
    #         traject_value = df_gather['parameter_input'].values[0]
    #         df['parameter_input'] = df['parameter_input'].apply(lambda x: traject_value if isna(x) else x)
    #
    #     # GIS spatial joins
    #     # TODO: Retrieve from geopackage
    #
    #     # Add to collection
    #     collection_of_dfs[parameter_name] = df


    ##
