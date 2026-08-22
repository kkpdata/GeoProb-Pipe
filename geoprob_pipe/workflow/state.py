import os
from typing import Optional, Dict
import sqlite3
from geopandas import GeoDataFrame, read_file
from pathlib import Path
from uuid import uuid4
from geoprob_pipe.utils.validation_messages import BColors
import fiona


class QuestionAnswer:
    """ The terminal user interface has a workflow of questions that the users answers. Based on this, and imported data
    GeoProb-Pipe determines the state of the application. The answers to these questions (this part of the state) are
    stored in the geopackage in table 'workflow_questions'. """

    def __init__(self, file_path: str):
        self.file_path: str = file_path

    def store(self, question_label: str, answer: str):
        """ This method stores the answer to a question. """

        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_questions (
                question_label TEXT PRIMARY KEY,
                answer TEXT
            )
        """)

        cursor.execute(f"""
            INSERT INTO workflow_questions (
                question_label,
                answer
            )
            VALUES (?, ?)
            ON CONFLICT(question_label)
            DO UPDATE SET answer = excluded.answer
        """, (question_label, answer))

        conn.commit()
        conn.close()

    def retrieve(self, question: str) -> Optional[str]:
        """ This method retrieves the answer to a question (if already stored). """
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT answer
                FROM workflow_questions
                WHERE question_label = '{question}'
                LIMIT 1;
            """)
        except sqlite3.OperationalError:  # table does not exist
            return None
        result = cursor.fetchone()
        if not result:
            return None
        return result[0]


class GeoDataFrames:

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: str = file_path
        self._read_geodataframes: Dict[str, GeoDataFrame] = {}

    def store(self, gdf: GeoDataFrame, layer_name: str):
        gdf.to_file(Path(self.file_path), layer=layer_name, driver="GPKG")
        print(f"{BColors.OKBLUE}"
              f"✅  Geografische tabel '{layer_name}' toegevoegd aan het GeoProb-Pipe GeoPackage.{BColors.ENDC}")

    def retrieve(self, layer_name: str) -> Optional[GeoDataFrame]:
        # First check if already retrieved before
        if layer_name in self._read_geodataframes.keys():
            return self._read_geodataframes[layer_name]

        # Otherwise retrieve from GeoProb-Pipe-file
        layers = fiona.listlayers(self.file_path)
        if layer_name not in layers:
            return None
        return read_file(self.file_path, layer=layer_name)

    @property
    def hrd_locations(self) -> Optional[GeoDataFrame]:
        return self.retrieve(layer_name="hrd_locations")


class DataFrames:

    def __init__(self):
        pass


def _if_needed_create_dummy_gpkg(file_path: Optional[str] = None, file_dir: Optional[str] = None) -> str:
    if (file_path is None and file_dir is None) or (file_path is not None and file_dir is not None):
        raise ValueError(f"Specify either the path to the GeoProb-Pipe-file, or a directory where a dummy can "
                         f"can be created.")
    elif file_dir is not None:
        import geopandas as gpd
        gdf = gpd.GeoDataFrame(geometry=[])
        path_to_gpkg = os.path.join(file_dir, f"dummy_{uuid4().__str__()}.geoprob_pipe.gpkg")
        gdf.to_file(Path(path_to_gpkg, driver="GPKG"))
        file_path = path_to_gpkg
    return file_path


class State:
    """ Through the terminal user interface the user selects choices/preferences (questions and answers) and imports
    data. The state of the application is the state of these answers and imported data. """

    def __init__(self, file_path: Optional[str] = None, file_dir: Optional[str | Path] = None):
        """

        :param file_path: Path to the GeoProb-Pipe file.
        """
        self.file_path: str = _if_needed_create_dummy_gpkg(file_path, file_dir)
        self.question_answer = QuestionAnswer(self.file_path)
        self.gdf = GeoDataFrames(self.file_path)
        self.df = DataFrames()
