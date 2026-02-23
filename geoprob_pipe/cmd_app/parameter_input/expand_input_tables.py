from typing import Dict, List
from pandas import DataFrame, isna, notna, concat, read_sql, read_csv
import sqlite3
import numpy as np
import os
import scipy.stats as sct
from geopandas import GeoDataFrame, read_file
from geoprob_pipe.calculations.systems.mappers.initial_input_mapper import INITIAL_INPUT_MAPPER
from geoprob_pipe.cmd_app.parameter_input.input_parameter_tables import InputParameterTables
from probabilistic_library import FragilityValue


def _combine_parameter_invoer_sources(tables: InputParameterTables) -> DataFrame:
    """ Combineert de geo-gerefereerde parameter invoer met de handmatige invoer die oorspronkelijk uit de Excel kwam.
    Zodoende kan vanuit één dataframe de invoer geëxplodeerd worden naar invoer per uittredepunt. """

    # Gather raw data
    df_gis_join_parameter_invoer = tables.df_gis_join_parameter_invoer
    df_gis_join_parameter_invoer['scope'] = 'gis_uittredepunt'
    df_parameter_invoer = tables.df_parameter_invoer

    # Concatenate
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        df_parameter_invoer_combined = concat(
            [df_gis_join_parameter_invoer, df_parameter_invoer], ignore_index=True)

    return df_parameter_invoer_combined


def _gather_hrd_frag_line_from_geopackage(ref: str, geopackage_filepath: str):
    # Read database
    conn = sqlite3.connect(geopackage_filepath)
    df_frag_line: DataFrame = read_sql(
        sql=f"SELECT * FROM fragility_values_invoer_hrd WHERE fragility_values_ref = '{ref}' AND kans < 1.0;",
        con=conn)
    conn.close()

    # Filter beta > 8 (probabilistic library cannot work with that in 26.1.1)
    df_frag_line['beta'] = -sct.norm.ppf(df_frag_line['kans'])
    df_frag_line = df_frag_line[df_frag_line['beta'] < 8.0].copy(deep=True)
    df_frag_line = df_frag_line.drop(columns=["beta"])

    # Validate
    assert df_frag_line.__len__() > 2
    # It should be validated beforehand that all added fragility lines are at least 3 points. So if this assert triggers
    # something should be improved earlier in validation.

    # Construct Fragility Values
    df_frag_line = df_frag_line.sort_values(by=["waarde"])
    frag_points = []
    for index, row in df_frag_line.iterrows():
        fc = FragilityValue()
        fc.x = row["waarde"]
        fc.probability_of_failure = row["kans"]
        frag_points.append(fc)

    return frag_points


def _gather_frag_line_from_csv(csv_file_name: str, geopackage_filepath: str):

    # Read csv-file
    csv_dir = os.path.join(os.path.dirname(geopackage_filepath), "frag_csv_files")
    os.makedirs(csv_dir, exist_ok=True)
    path_to_csv = os.path.join(csv_dir, csv_file_name)
    if not os.path.exists(path_to_csv):
        raise FileNotFoundError(
            f"CSV-file with fragility curve not found for reference '{csv_file_name}'. Please make sure to place your "
            f"csv-files at the following location: \n{csv_dir}")
    df_frag_line = read_csv(path_to_csv, sep=",")

    # Validate
    assert df_frag_line.__len__() > 2
    # It should be validated beforehand that all added fragility lines are at least 3 points. So if this assert triggers
    # something should be improved earlier in validation.

    # Construct Fragility Values
    df_frag_line = df_frag_line.sort_values(by=["waarde"])
    frag_points = []
    for index, row in df_frag_line.iterrows():
        fc = FragilityValue()
        fc.x = row["waarde"]
        fc.probability_of_failure = row["kans"]
        frag_points.append(fc)

    return frag_points


def _collect_fragility_values(
        tables: InputParameterTables, fragility_refs: List[str], geopackage_filepath: str,
) -> DataFrame:
    """ Collects the fragility values from the different sources. The sources are (a) the HRD-file, (b) the Excel input
    file, and (c) the csv folder.

    :param tables:
    :param fragility_refs:
    :param geopackage_filepath:
    :return: Returns a dataframe with columns fragility_values_ref and fragility_values.
    """

    df_frag_invoer = tables.df_fragility_values_invoer
    available_frag_invoer_refs = df_frag_invoer['fragility_values_ref'].unique()
    return_array = []
    for fragility_ref in fragility_refs:

        # From .csv-file (not stored in GeoPackage)
        if fragility_ref.endswith(".csv"):
            return_array.append({
                "fragility_values_ref": fragility_ref,
                "fragility_values": _gather_frag_line_from_csv(
                    csv_file_name=fragility_ref, geopackage_filepath=geopackage_filepath)})

        # From HRD-database (previously stored in GeoPackage)
        elif fragility_ref not in available_frag_invoer_refs:
            return_array.append({
                "fragility_values_ref": fragility_ref,
                "fragility_values": _gather_hrd_frag_line_from_geopackage(
                    ref=fragility_ref, geopackage_filepath=geopackage_filepath)})

        # Otherwise, retrieve custom curve from Excel (previously stored in GeoPackage)
        else:
            raise NotImplementedError(f"Should now retrieve it from the df_frag_invoer.")  # TODO

    # Build dataframe
    if return_array.__len__() == 0:
        df = DataFrame(data=[], columns=["fragility_values_ref", "fragility_values"])
        return df
    return DataFrame(return_array)


def _add_fragility_values_to_combined_parameter_invoer(
        df_parameter_invoer_combined: DataFrame, tables: InputParameterTables, geopackage_filepath: str, drop_ref: bool = True) -> DataFrame:
    """ Haalt uit de fragility values Excel de arrays op en vervang in de df_parameter_invoer_combined de referentie
    met de daadwerkelijke fragility values. """

    df = df_parameter_invoer_combined.copy(deep=True)

    # Replace empty values with NaN
    df['fragility_values_ref'] = df['fragility_values_ref'].replace('', np.nan)
    df['fragility_values_ref'] = df['fragility_values_ref'].infer_objects(copy=False)

    # Gather referenced fragility value refs
    fragility_refs = df['fragility_values_ref'].dropna().unique()

    # Collect fragility lines
    df_frag_lines = _collect_fragility_values(
        tables=tables, fragility_refs=fragility_refs, geopackage_filepath=geopackage_filepath)

    # Attach to parameter invoer df
    df = df.merge(
        df_frag_lines, left_on="fragility_values_ref", right_on="fragility_values_ref", how="left")

    if drop_ref:
        df = df.drop(columns=["fragility_values_ref"])

    return df


def _collect_right_columns_combined_parameter_invoer(df_parameter_invoer_combined: DataFrame) -> DataFrame:
    """ Parameter tabel omzetten naar juiste kolommen. Enkel per uittredepunt, scenario en parameter de
    parameterinvoer. """

    # Add parameter invoer: op uittredepunten niveau
    df_parameter_invoer_combined = df_parameter_invoer_combined.drop(columns=["bronnen", "opmerking"])
    parameter_description_columns = [
        "distribution_type", "mean", "variation", "deviation", "minimum", "maximum", "fragility_values"]
    if "fragility_values_ref" in df_parameter_invoer_combined.columns:
        parameter_description_columns.append("fragility_values_ref")
    df_parameter_invoer_combined['parameter_input'] = df_parameter_invoer_combined.apply(lambda row: {
        k: row[k] for k in parameter_description_columns if isinstance(row[k], list) or notna(row[k])
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
    df_dummy_data = DataFrame(INITIAL_INPUT_MAPPER[model_string]['input'])

    _ = df_dummy_data.sort_values(by=["name"])
    df_dummy_data = df_dummy_data.sort_values(by=["name"])
    return df_dummy_data['name'].unique().tolist()
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

    # return ["mv_exit", "gamma_sat_deklaag"]  # TODO
    # return ["gamma_sat_deklaag"]  # TODO


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
            (df_parameter_invoer_combined['scope'] == 'gis_uittredepunt')].copy(deep=True)
        df_gather = df_gather[["scope_referentie", "parameter_input"]]
        df_gather = df_gather.rename(columns={"scope_referentie": "uittredepunt_id"})
        df['parameter_input'] = df['parameter_input'].combine_first(
            df_identifiers.copy(deep=True).merge(df_gather, on=["uittredepunt_id"], how="left")['parameter_input'])

        # Add to collection
        collection_of_dfs[parameter_name] = df

    return collection_of_dfs


def _concat_collection(collection: Dict[str, DataFrame]):
    for parameter_name, df in collection.items():
        collection[parameter_name]['parameter_name'] = parameter_name
    return_df = concat([df for _, df in collection.items()], ignore_index=True)
    return_df = return_df.rename(columns={"naam": "ondergrondscenario_naam"})
    return return_df[["parameter_name", "vak_id", "uittredepunt_id", "ondergrondscenario_naam", "parameter_input"]]


def run_expand_input_tables(geopackage_filepath: str, add_frag_ref: bool = False) -> DataFrame:
    """

    :param geopackage_filepath:
    :param add_frag_ref: Indien True, dan wordt voor parameter input met een distribution_type 'cdf_curve' de referentie
        naar de invoer behouden. Deze is niet nodig voor de berekeningen, maar wordt wel gebruikt voor de visualisaties.
    :return:
    """
    tables = InputParameterTables(geopackage_filepath=geopackage_filepath)
    df_identifiers = _construct_df_identifiers(geopackage_filepath=geopackage_filepath, tables=tables)

    # Construct df_parameter_invoer_combined
    df_parameter_invoer_combined1 = _combine_parameter_invoer_sources(tables=tables)
    df_parameter_invoer_combined2 = _add_fragility_values_to_combined_parameter_invoer(
        df_parameter_invoer_combined=df_parameter_invoer_combined1, tables=tables,
        geopackage_filepath=geopackage_filepath, drop_ref=add_frag_ref==False)
    df_parameter_invoer_combined3 = _collect_right_columns_combined_parameter_invoer(
        df_parameter_invoer_combined=df_parameter_invoer_combined2)

    # Expand
    collection: Dict[str, DataFrame] = _expand(
        df_parameter_invoer_combined=df_parameter_invoer_combined3,
        df_identifiers=df_identifiers,
        geopackage_filepath=geopackage_filepath)

    return _concat_collection(collection=collection)
