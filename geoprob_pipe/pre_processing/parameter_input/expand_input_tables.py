from typing import Dict, List
from pandas import DataFrame, isna, notna, concat
import sqlite3
import numpy as np
from geopandas import GeoDataFrame, read_file
from geoprob_pipe.calculations.system_calculations import SYSTEM_CALCULATION_MAPPER
from geoprob_pipe.pre_processing.parameter_input.input_parameter_tables import InputParameterTables


def _combine_parameter_invoer_sources(tables: InputParameterTables):

    # Gather raw data
    df_gis_join_parameter_invoer = tables.df_gis_join_parameter_invoer
    df_gis_join_parameter_invoer['scope'] = 'gis_uittredepunt'
    df_parameter_invoer = tables.df_parameter_invoer

    # Concatenate
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        df_parameter_invoer_combined = concat([df_gis_join_parameter_invoer, df_parameter_invoer], ignore_index=True)

    return df_parameter_invoer_combined


def _add_fragility_values_to_combined_parameter_invoer(df_parameter_invoer_combined: DataFrame) -> DataFrame:

    df = df_parameter_invoer_combined.copy(deep=True)

    # Replace empty values with NaN
    df['fragility_values_ref'] = df['fragility_values_ref'].replace('', np.nan)
    df['fragility_values_ref'] = df['fragility_values_ref'].infer_objects(copy=False)

    # Gather referenced fragility value refs
    fragility_refs = df['fragility_values_ref'].dropna().unique()

    # Collect fragility lines
    df_frag_lines = DataFrame(
        data={"fragility_values_ref": fragility_refs, "fragility_values": ["TODO"] * fragility_refs.__len__()})
    # TODO: Collecting should still be done. This is just a temporary value of 'TODO'

    # Attach to parameter invoer df
    df = df.merge(
        df_frag_lines, left_on="fragility_values_ref", right_on="fragility_values_ref", how="left")
    df = df.drop(columns=["fragility_values_ref"])

    return df


def _collect_right_columns_combined_parameter_invoer(df_parameter_invoer_combined: DataFrame) -> DataFrame:
    """ Parameter tabel omzetten naar juiste kolom onderdelen """

    # Add parameter invoer: op uittredepunten niveau
    df_parameter_invoer_combined = df_parameter_invoer_combined.drop(columns=["bronnen", "opmerking"])
    parameter_description_columns = [
        "distribution_type", "mean", "variation", "deviation", "minimum", "maximum", "fragility_values"]
    df_parameter_invoer_combined['parameter_input'] = df_parameter_invoer_combined.apply(lambda row: {
        k: row[k] for k in parameter_description_columns if notna(row[k])
    }, axis=1)
    df_parameter_invoer_combined = df_parameter_invoer_combined.drop(columns=parameter_description_columns)
    return df_parameter_invoer_combined


def _construct_df_identifiers(geopackage_filepath: str, tables: InputParameterTables):
    """ Create identifiers table.

    The identifiers table is a table with unique rows (unique uittredepunt, vak and scenario combo). It is used as a
    base to explode to input per scenario and uittredepunt. """

    gdf_uittredepunten: GeoDataFrame = read_file(geopackage_filepath, layer="uittredepunten")
    df_identifiers: DataFrame = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df_scenario_invoer: DataFrame = tables.df_scenario_invoer
    df_identifiers = df_identifiers.merge(df_scenario_invoer, left_on="vak_id", right_on="vak_id")
    df_identifiers = df_identifiers.drop(columns=["kans"])
    return df_identifiers


def _gather_required_input_parameters(geopackage_filepath: str) -> List[str]:

    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT geoprob_pipe_metadata."values" 
        FROM geoprob_pipe_metadata 
        WHERE metadata_type='geohydrologisch_model';
    """)
    result = cursor.fetchone()
    if not result:
        raise ValueError
    model_string = result[0]
    conn.close()
    df_dummy_data = DataFrame(SYSTEM_CALCULATION_MAPPER[model_string]['dummy_invoer'])

    _ = df_dummy_data.sort_values(by=["name"])
    # df_dummy_data = df_dummy_data.sort_values(by=["name"])
    # return df_dummy_data['name'].unique().tolist()
    # TODO: Return this to use in iteration to retrieve data

    # Method to use the system_function. Not necessary because of the dummy input. But for now kept.
    # from geoprob_pipe.calculations.system_calculations.piping_moria.reliability_calculation import \
    #     PipingMORIASystemReliabilityCalculation
    # from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import PIPING_DUMMY_INPUT
    # import inspect
    #
    # reliability_calculation = PipingMORIASystemReliabilityCalculation(PIPING_DUMMY_INPUT)
    # sig = inspect.signature(reliability_calculation.given_system_variables_setup_function)
    # _ = [
    #     name for name, param in sig.parameters.items()
    #     if param.default == inspect.Parameter.empty and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
    # ]

    return ["mv_exit", "gamma_sat_deklaag"]  # TODO


def _expand(df_parameter_invoer_combined: DataFrame, df_identifiers: DataFrame, geopackage_filepath: str) -> Dict[str, DataFrame]:

    # Add parameter invoer: op uittredepunten niveau
    required_input_parameters = _gather_required_input_parameters(geopackage_filepath=geopackage_filepath)
    collection_of_dfs: Dict[str, DataFrame] = {}
    for parameter_name in required_input_parameters:

        # Gather and merge input on uittredepunten-niveau
        df_gather = df_parameter_invoer_combined[
            (df_parameter_invoer_combined['parameter'] == parameter_name) &
            (df_parameter_invoer_combined['scope'] == 'uittredepunt')]
        df_gather = df_gather[["scope_referentie", "parameter_input"]]
        df = df_identifiers.copy(deep=True).merge(
            df_gather, how="left", left_on="uittredepunt_id", right_on="scope_referentie")
        df = df.drop(columns=["scope_referentie"])

        # Vak / scenario niveau
        df_gather = df_parameter_invoer_combined[
            (df_parameter_invoer_combined['parameter'] == parameter_name) &
            (df_parameter_invoer_combined['scope'] == 'vak') &
            (df_parameter_invoer_combined['ondergrondscenario_naam'].notna())]
        df_gather = df_gather[["scope_referentie", "ondergrondscenario_naam", "parameter_input"]]
        df_gather = df_gather.rename(columns={
            "scope_referentie": "vak_id",
            "ondergrondscenario_naam": "naam"})
        df['parameter_input'] = df['parameter_input'].combine_first(
            df_identifiers.copy(deep=True).merge(df_gather, on=["vak_id", "naam"], how="left")['parameter_input'])

        # Vak niveau
        df_gather = df_parameter_invoer_combined[
            (df_parameter_invoer_combined['parameter'] == parameter_name) &
            (df_parameter_invoer_combined['scope'] == 'vak') &
            (df_parameter_invoer_combined['ondergrondscenario_naam'].isna())]
        df_gather = df_gather[["scope_referentie", "parameter_input"]]
        df_gather = df_gather.rename(columns={"scope_referentie": "vak_id"})
        df['parameter_input'] = df['parameter_input'].combine_first(
            df_identifiers.copy(deep=True).merge(df_gather, on=["vak_id"], how="left")['parameter_input'])

        # Traject niveau
        df_gather = df_parameter_invoer_combined[
            (df_parameter_invoer_combined['parameter'] == parameter_name) &
            (df_parameter_invoer_combined['scope'] == 'traject')]
        if df_gather.__len__() >= 1:
            traject_value = df_gather['parameter_input'].values[0]
            df['parameter_input'] = df['parameter_input'].apply(lambda x: traject_value if isna(x) else x)

        # GIS spatial joins
        df_gather = df_parameter_invoer_combined[
            (df_parameter_invoer_combined['parameter'] == parameter_name) &
            (df_parameter_invoer_combined['scope'] == 'gis_uittredepunt')]
        df_gather = df_gather[["scope_referentie", "parameter_input"]]
        df = df_identifiers.copy(deep=True).merge(
            df_gather, how="left", left_on="uittredepunt_id", right_on="scope_referentie")
        df = df.drop(columns=["scope_referentie"])

        # Add to collection
        collection_of_dfs[parameter_name] = df

    return collection_of_dfs



geopackage_filepath = r"C:\Users\CP\Downloads\C_Analyse_corr\16-1\TestGISInvoer5.geoprob_pipe.gpkg"


# def run_expand_input_tables(geopackage_filepath: str) -> DataFrame:
tables = InputParameterTables(geopackage_filepath=geopackage_filepath)
df_identifiers = _construct_df_identifiers(geopackage_filepath=geopackage_filepath, tables=tables)

# Construct df_parameter_invoer_combined
df_parameter_invoer_combined = _combine_parameter_invoer_sources(tables=tables)
df_parameter_invoer_combined = _add_fragility_values_to_combined_parameter_invoer(
    df_parameter_invoer_combined=df_parameter_invoer_combined)
df_parameter_invoer_combined = _collect_right_columns_combined_parameter_invoer(
    df_parameter_invoer_combined=df_parameter_invoer_combined)

df_tmp = df_parameter_invoer_combined[df_parameter_invoer_combined["parameter"] == "mv_exit"].copy(deep=True)

##

# Expand
collection: Dict[str, DataFrame] = _expand(
    df_parameter_invoer_combined=df_parameter_invoer_combined,
    df_identifiers=df_identifiers,
    geopackage_filepath=geopackage_filepath)

    # return DataFrame()  # TODO: Merge collection retrieved from the above expansion


