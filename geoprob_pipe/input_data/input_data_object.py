from __future__ import annotations
from geopandas import GeoDataFrame, read_file
from pandas import read_sql, DataFrame
from probabilistic_library import FragilityValue
import pydra_core as pydra
from shapely import Point
# from geoprob_pipe.input_data.vak import VakCollection
# from geoprob_pipe.input_data.ondergrond_scenario import OndergrondScenarioCollection
# from geoprob_pipe.input_data.uittredepunt import UittredepuntCollection
# from geoprob_pipe.input_data.overschrijdingsfrequentielijn import OverschrijdingsfrequentielijnCollection
# from geoprob_pipe.utils.workspace import Workspace
# from geoprob_pipe.input_data.data_validation import checks_input_parameters, checks_overview_parameters
# noinspection PyPep8Naming
# from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
from typing import Optional, TYPE_CHECKING, List
import sqlite3
from geoprob_pipe.misc.traject_normering import TrajectNormering
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
    # from geoprob_pipe import GeoProbPipe


class Vak:

    def __init__(self, app_settings: ApplicationSettings, vak_id: int):
        self.app_settings: ApplicationSettings = app_settings
        self.vak_id = vak_id


class Uittredepunten:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings
        self.gdf: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    def uittredepunt(self, uittredepunt_id: int):
        row = self.gdf.loc[self.gdf['uittredepunt_id'] == uittredepunt_id].iloc[0]
        kwargs = row.to_dict()
        return Uittredepunt(self.app_settings, **kwargs)


class Uittredepunt:

    def __init__(
            self, app_settings: ApplicationSettings, geometry: Point, uittredepunt_id: int, vak_id: int, **_):
        self.app_settings: ApplicationSettings = app_settings
        self.geometry: Point = geometry
        self.uittredepunt_id: int = uittredepunt_id
        self.vak_id: int = vak_id

    # def _get_vak_id(self) -> int:
    #     conn = sqlite3.connect(self.app_settings.geopackage_filepath)
    #     cursor = conn.cursor()
    #     cursor.execute(f"SELECT vak_id FROM uittredepunten WHERE uittredepunt_id = {self.uittredepunt_id};")
    #     result = cursor.fetchone()
    #     if result:
    #         conn.close()
    #         return result[0]
    #     raise ValueError

    @property
    def vak(self) -> Vak:
        return Vak(app_settings=self.app_settings, vak_id=self.vak_id)


class Scenarios:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings
        self.df = self._query_scenarios()

    def _query_scenarios(self) -> DataFrame:
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        df_scenario_invoer = read_sql("SELECT * FROM scenario_invoer;", conn)
        df_scenario_invoer = df_scenario_invoer[["vak_id", "naam", "kans"]]
        conn.close()
        return df_scenario_invoer

    def scenario_kans(self, vak_id: int, scenario_naam: str) -> float:
        kans: float = self.df[
            (self.df['vak_id'] == vak_id) &
            (self.df['naam'] == scenario_naam)
        ]['kans'].iloc[0]
        return kans


class HydraNLData:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings
        self.gdf_locations: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="hrd_locaties")

    def hrd_fragility_values(self, ref: str) -> List[FragilityValue]:

        # Read from geopackage
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        df_frag_line = read_sql(
            f"SELECT * FROM fragility_values_invoer_hrd WHERE fragility_values_ref = '{ref}';",
            conn)
        conn.close()

        # Construct Fragility Values
        df_frag_line = df_frag_line.sort_values(by=["waarde"])
        frag_points = []
        for index, row in df_frag_line.iterrows():
            fc = FragilityValue()
            fc.x = row["waarde"]
            fc.probability_of_failure = row["kans"]
            frag_points.append(fc)

        return frag_points

    # noinspection PyUnresolvedReferences
    def hrd_frequency_line(self, ref: str) -> pydra.core.datamodels.frequency_line.FrequencyLine:
        hrd_fragility_values = self.hrd_fragility_values(ref=ref)
        level = [item.x for item in hrd_fragility_values]
        exceedance_frequency = [item.probability_of_failure for item in hrd_fragility_values]
        # noinspection PyUnresolvedReferences
        return pydra.core.datamodels.frequency_line.FrequencyLine(
            level=level, exceedance_frequency=exceedance_frequency)


class Vakken:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings
        self.gdf: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")


class InputData:
    """ Subclass to group input data of vakken, uittredepunten and ondergrondscenarios. Data is retrieved from the input
    Excel-file. """

    def __init__(
            self,
            app_settings: ApplicationSettings
            # workspace: Workspace,
    ):

        self.app_settings: ApplicationSettings = app_settings
        # self.workspace: Workspace = workspace

        # # Read overview data of parameters from input Excel file (includes e.g. upper and lower bounds, type of
        # # distribution, etc.) and carry out checks
        # self.df_overview_parameters = pd.read_excel(
        #     workspace.path_input_excel, sheet_name="Overzicht_parameters",
        #     index_col=0, header=0).rename(columns=lambda x: x.strip())
        # checks_overview_parameters(self.df_overview_parameters)
        #
        # # Collections
        # self.vakken = VakCollection(workspace=workspace, df_overview_parameters=self.df_overview_parameters)
        # self.uittredepunten = UittredepuntCollection(
        #     workspace=workspace, vak_collection=self.vakken, df_overview_parameters=self.df_overview_parameters)
        # self.ondergrondscenarios = OndergrondScenarioCollection(
        #     workspace=workspace, vak_collection=self.vakken, df_overview_parameters=self.df_overview_parameters)
        # checks_input_parameters(
        #     self.df_overview_parameters, self.vakken.df, self.uittredepunten.df, self.ondergrondscenarios.df)
        # logger.info(f"Parameter data successfully loaded from `{workspace.path_input_excel.name}`.")

        # Traject-data
        self._traject_normering: Optional[TrajectNormering] = None

        # # HRD-data
        # self.overschrijdingsfrequentielijnen = OverschrijdingsfrequentielijnCollection(
        #     path_hrd=workspace.path_hrd, uittredepunt_collection=self.uittredepunten)
        # logger.info(f"HRD .sqlite file successfully loaded from `{workspace.path_hrd.name}`.")

        self.uittredepunten = Uittredepunten(self.app_settings)
        self.scenarios = Scenarios(self.app_settings)
        self.vakken = Vakken(self.app_settings)
        self.hydra_nl_data = HydraNLData(self.app_settings)

    @property
    def geohydrologisch_model(self) -> str:
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
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
        return model_string

    @property
    def traject_normering(self):
        if self._traject_normering is None:
            self._traject_normering = TrajectNormering(hrd_path=self.app_settings.hrd_file_path)
        return self._traject_normering
