from geoprob_pipe.workflow.base_objects import Action
from geoprob_pipe.workflow.questions import QuestionImportHRD, QuestionDirHydraNLDatabase
from geoprob_pipe.cmd_app.spatial_layers.hrd.import_from_hrd import hrd_file_path
import sqlite3
from pandas import read_sql
from geopandas import GeoDataFrame, points_from_xy


class ActionImportHRDLocationsFromHydraNLDatabase(Action):

    def execute(self):
        dir_to_db = self.state.question_answer.retrieve(question=QuestionDirHydraNLDatabase.label)
        path_to_db = hrd_file_path(hrd_dir=dir_to_db)
        conn = sqlite3.connect(path_to_db)
        df = read_sql("SELECT Name, XCoordinate, YCoordinate FROM HRDLocations", conn)
        gdf = GeoDataFrame(df, geometry=points_from_xy(df["XCoordinate"], df["YCoordinate"]), crs="EPSG:28992")
        conn.close()
        gdf = gdf.drop(columns=["XCoordinate", "YCoordinate"])
        gdf = gdf.rename(columns={"Name": "location_name"})
        self.state.gdf.store(gdf=gdf, layer_name="hrd_locations")

    @property
    def should_run(self) -> bool:
        if not (self.state.question_answer.retrieve(QuestionImportHRD.label) == "Hydra-NL database" and
                self.state.question_answer.retrieve(QuestionDirHydraNLDatabase.label) is not None):
            return False
        return True

    @property
    def completed(self) -> bool:
        if self.state.gdf.hrd_locations is None:
            return False
        return True
