import sqlite3
from pandas import read_sql_query
from pandas import DataFrame
import numpy as np


def append_to_gis_join_parameter_invoer_table(df_sjoin: DataFrame, parameter_name: str, geopackage_filepath: str):
    """ Through mean only """

    assert df_sjoin.columns.__len__() == 2
    assert "mean" in df_sjoin.columns
    assert "uittredepunt_id" in df_sjoin.columns

    # Create other columns
    df_to_append = df_sjoin.copy(deep=True)
    df_to_append = df_to_append.rename(columns={"uittredepunt_id": "scope_referentie"})
    df_to_append["parameter"] = parameter_name
    df_to_append["scope"] = "uittredepunt"
    df_to_append["ondergrondscenario_naam"] = ""
    df_to_append["distribution_type"] = "deterministic"
    df_to_append["variation"] = np.nan
    df_to_append["deviation"] = np.nan
    df_to_append["minimum"] = np.nan
    df_to_append["maximum"] = np.nan
    df_to_append["fragility_values_ref"] = ""
    df_to_append["bronnen"] = ""
    df_to_append["opmerking"] = ""

    # Sort columns
    df_to_append = df_to_append[
        ["parameter", "scope", "scope_referentie", "ondergrondscenario_naam", "distribution_type", "mean", "variation",
         "deviation", "minimum", "maximum", "fragility_values_ref", "bronnen", "opmerking"]]

    # Get table names
    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_names = [row[0] for row in cursor.fetchall()]

    # If gis_join-table is non-existent yet
    if "gis_join_parameter_invoer" not in tables_names:
        df_to_append.to_sql("gis_join_parameter_invoer", conn, if_exists="replace", index=False)
        return
    # If polderpeil not yet in gis_join-table
    df_existing = read_sql_query("SELECT * FROM gis_join_parameter_invoer;", conn)
    if parameter_name not in df_existing['parameter'].unique():
        df_to_append.to_sql("gis_join_parameter_invoer", conn, if_exists="append", index=False)
        return
    raise ValueError
    # Should not have come here. Parameter should already be supplied, and thus user should not have been able to
    # make a new spatial join.


def append_hrd_to_gis_join_parameter_invoer_table(df_sjoin: DataFrame, geopackage_filepath: str):
    """ Through mean only """

    assert df_sjoin.columns.__len__() == 2
    assert "hrd_name" in df_sjoin.columns
    assert "uittredepunt_id" in df_sjoin.columns

    # Create other columns
    df_to_append = df_sjoin.copy(deep=True)
    df_to_append["parameter"] = "buitenwaterstand"
    df_to_append["scope"] = "uittredepunt"
    df_to_append = df_to_append.rename(columns={"uittredepunt_id": "scope_referentie"})
    df_to_append["ondergrondscenario_naam"] = ""
    df_to_append["distribution_type"] = "cdf_curve"
    df_to_append["mean"] = np.nan
    df_to_append["variation"] = np.nan
    df_to_append["deviation"] = np.nan
    df_to_append["minimum"] = np.nan
    df_to_append["maximum"] = np.nan
    df_to_append = df_to_append.rename(columns={"hrd_name": "fragility_values_ref"})
    df_to_append["bronnen"] = ""
    df_to_append["opmerking"] = ""

    # Sort columns
    df_to_append = df_to_append[
        ["parameter", "scope", "scope_referentie", "ondergrondscenario_naam", "distribution_type", "mean", "variation",
         "deviation", "minimum", "maximum", "fragility_values_ref", "bronnen", "opmerking"]]

    # Get table names
    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_names = [row[0] for row in cursor.fetchall()]

    # If gis_join-table is non-existent yet
    if "gis_join_parameter_invoer" not in tables_names:
        df_to_append.to_sql("gis_join_parameter_invoer", conn, if_exists="replace", index=False)
        return
    # If polderpeil not yet in gis_join-table
    df_existing = read_sql_query("SELECT * FROM gis_join_parameter_invoer;", conn)
    if "polderpeil" not in df_existing['parameter'].unique():
        df_to_append.to_sql("gis_join_parameter_invoer", conn, if_exists="append", index=False)
        return
    raise ValueError
    # Should not have come here. Parameter should already be supplied, and thus user should not have been able to
    # make a new spatial join.
