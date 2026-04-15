from __future__ import annotations
import scipy.stats as sct
from pandas import DataFrame, read_sql_query
from shapely import LineString, MultiLineString
import sqlite3
from typing import Tuple, Optional, TYPE_CHECKING, Dict, List
from geopandas import read_file, GeoDataFrame
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _data_from_metadata_table(app_settings: ApplicationSettings) -> Tuple[str, bool, int, int, float]:
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df: DataFrame = read_sql_query("SELECT * FROM geoprob_pipe_metadata;", conn)
    conn.close()

    traject_id = df[df["metadata_type"] == "traject_id"]["values"].values[0]
    signaleringswaarde = int(df[df["metadata_type"] == "signaleringswaarde"]["values"].values[0])
    ondergrens = int(df[df["metadata_type"] == "ondergrens"]["values"].values[0])
    w = float(df[df["metadata_type"] == "w"]["values"].values[0])
    is_bovenrivierengebied = bool(int(df[df["metadata_type"] == "is_bovenrivierengebied"]["values"].values[0]))

    return traject_id, is_bovenrivierengebied, signaleringswaarde, ondergrens, w


def _get_traject_length(app_settings: ApplicationSettings) -> float:
    gdf_dijktraject: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="dijktraject")
    gdf_dijktraject_geom = gdf_dijktraject.iloc[0].geometry
    if isinstance(gdf_dijktraject_geom, MultiLineString):
        assert gdf_dijktraject_geom.geoms.__len__() == 1
        ls_dijktraject: LineString = gdf_dijktraject_geom.geoms[0]
    elif isinstance(gdf_dijktraject_geom, LineString):
        ls_dijktraject: LineString = gdf_dijktraject_geom
    else:
        raise NotImplementedError(f"Type of {type(gdf_dijktraject_geom)} is not yet implemented.")
    return ls_dijktraject.length


class TrajectNormering:
    """ Gathers the traject id and calculates the traject normering
    from the HRD-files.
    """

    def __init__(self, app_settings: ApplicationSettings, norm_is_ondergrens: bool = True):

        # Input
        self.traject_naam: Optional[str] = None  # Placeholder for future implementation

        # Parameters
        traject_id, is_bovenrivierengebied, signaleringswaarde, ondergrens, w = _data_from_metadata_table(
            app_settings=app_settings)
        self.bovenrivierengebied: bool = is_bovenrivierengebied
        self.traject_id: str = traject_id
        self.signaleringswaarde: int = signaleringswaarde
        self.ondergrens: int = ondergrens
        self.w: float = w
        self.traject_lengte: float = _get_traject_length(app_settings=app_settings)
        self.faalkanseis_signaleringswaarde = 1.0 / self.signaleringswaarde
        self.faalkanseis_ondergrens = 1.0 / self.ondergrens
        self.faalkanseis_norm = self.faalkanseis_ondergrens
        if not norm_is_ondergrens:
            self.faalkanseis_norm = self.signaleringswaarde
        self.beta_norm = sct.norm.ppf(self.faalkanseis_norm)
        self.n_dsn = 1 + (0.9 * self.traject_lengte) / 300.0
        if not self.bovenrivierengebied:
            self.n_dsn = 1 + (0.4 * self.traject_lengte) / 300.0
        # TODO Nu Must Klein: Eigenlijk hoofdletter N_dsn.
        # Maar ipv afkorting naam gebruiken?
        self.faalkanseis_sign_dsn = (
            self.w * self.faalkanseis_signaleringswaarde) / self.n_dsn
        self.beta_sign_dsn = sct.norm.ppf(self.faalkanseis_sign_dsn)
        self.faalkanseis_ond_dsn = (
            self.w * self.faalkanseis_ondergrens) / self.n_dsn
        self.beta_ond_dsn = sct.norm.ppf(self.faalkanseis_ond_dsn)
        self.beta_categorie_grenzen = {
            "I": [-1 * sct.norm.ppf(self.faalkanseis_sign_dsn / 30), 50],
            "II": [
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn),
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn / 30),
            ],
            "III": [
                -1 * sct.norm.ppf(self.faalkanseis_ond_dsn),
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn),
            ],
            "IV": [
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens),
                -1 * sct.norm.ppf(self.faalkanseis_ond_dsn),
            ],
            "V": [
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens * 30),
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens),
            ],
            "VI": [
                -50,
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens * 30),
            ],
        }

        # Riskeer categorie grenzen
        cat_min3_upper_bound = -1 * sct.norm.ppf(self.faalkanseis_ondergrens * 10)
        lower_bound = 2.0
        if cat_min3_upper_bound < lower_bound:
            lower_bound = cat_min3_upper_bound - 0.5
        self.riskeer_categorie_grenzen: Dict[str, List] = {
            "+III": [-1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 1000), 20.0],
            "+II": [
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 100),
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 1000)
            ],
            "+I": [
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 10),
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 100)
            ],
            "0": [
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde),
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde / 10)
            ],
            "-I": [
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens),
                -1 * sct.norm.ppf(self.faalkanseis_signaleringswaarde),
            ],
            "-II": [cat_min3_upper_bound, -1 * sct.norm.ppf(self.faalkanseis_ondergrens)],
            "-III": [lower_bound, cat_min3_upper_bound],
        }
