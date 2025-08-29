import os.path
import scipy.stats as sct
import sqlite3
from typing import Tuple, Optional
from shapely import LineString
import importlib.resources
from geopandas import read_file, GeoDataFrame


def _get_traject_id(hrd_path: str, hlcd_path: str) -> Tuple[int, str]:
    """ Queries first the HRD for the integer ID of the traject. Then queries the HLCD to find the textual traject ID.
    """
    conn = sqlite3.connect(hrd_path)
    cursor = conn.cursor()
    query = "SELECT TrackID FROM General;"
    cursor.execute(query)
    track_id = cursor.fetchone()[0]
    conn.close()

    conn = sqlite3.connect(hlcd_path)
    cursor = conn.cursor()
    query = f"SELECT Name FROM Tracks WHERE TrackID={track_id};"
    cursor.execute(query)
    traject_id = cursor.fetchone()[0]
    conn.close()

    return track_id, traject_id


def _query_dijktrajecten(traject_id: str):
    """ Queries the dijktrajecten.shp that was retrieved from the API of the Waterveiligheidsportaal [1].

    [1] https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/fa4cc54e-26b3-4f25-b643-59458622901c
    """
    with importlib.resources.path('geoprob_pipe.misc.dijktrajecten', 'dijktrajecten.shp') as shp_path:
        gdf: GeoDataFrame = read_file(shp_path)
    gdf = gdf[gdf['TRAJECT_ID'] == traject_id]
    assert gdf.__len__() == 1, f"Only one traject id should have been found. Address this issue."
    geom: LineString = gdf.iloc[0].geometry
    return gdf.iloc[0]['NORM_SW'], gdf.iloc[0]['NORM_OG'], geom.length


class TrajectNormering:
    """ Gathers the traject id and calculates the traject normering from the HRD-files. """

    def __init__(
            self,
            hrd_path: str,
            traject_naam: Optional[str] = None,  # Non-existent in HRD? For now as optional parameter.
            norm_is_ondergrens: bool = True,
            bovenrivierengebied: bool = True,  # Where to find this? For now as manual parameter
    ):

        # Input
        self.traject_naam: Optional[str] = traject_naam
        self.hrd_path = hrd_path
        self.hlcd_path = os.path.join(os.path.dirname(self.hrd_path), "hlcd.sqlite")
        self.bovenrivierengebied: bool = bovenrivierengebied

        # Parameters
        self.traject_id: str = _get_traject_id(self.hrd_path, self.hlcd_path)[1].strip()
        signaleringswaarde, ondergrens, traject_lengte = _query_dijktrajecten(self.traject_id)
        self.signaleringswaarde: int = signaleringswaarde
        self.ondergrens: int = ondergrens
        self.w: float = 0.24
        self.traject_lengte: float = traject_lengte
        self.faalkanseis_signaleringswaarde = 1.0 / self.signaleringswaarde
        self.faalkanseis_ondergrens = 1.0 / self.ondergrens
        self.faalkanseis_norm = self.faalkanseis_ondergrens
        if not norm_is_ondergrens:
            self.faalkanseis_norm = self.signaleringswaarde
        self.beta_norm = sct.norm.ppf(self.faalkanseis_norm)
        self.n_dsn = 1 + (0.9 * self.traject_lengte) / 300.0
        if not self.bovenrivierengebied:
            self.n_dsn = 1 + (0.4 * self.traject_lengte) / 300.0
        # TODO Nu Must Klein: Eigenlijk hoofdletter N_dsn. Maar ipv afkorting naam gebruiken?
        self.faalkanseis_sign_dsn = (self.w * self.faalkanseis_signaleringswaarde) / self.n_dsn
        self.beta_sign_dsn = sct.norm.ppf(self.faalkanseis_sign_dsn)
        self.faalkanseis_ond_dsn = (self.w * self.faalkanseis_ondergrens) / self.n_dsn
        self.beta_ond_dsn = sct.norm.ppf(self.faalkanseis_ond_dsn)
        self.beta_categorie_grenzen = {
            "I": [
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn / 30),
                50
            ],
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
