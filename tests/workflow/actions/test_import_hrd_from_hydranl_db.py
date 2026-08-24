from geoprob_pipe.workflow import State
from geoprob_pipe.workflow.actions import ActionImportHRDLocationsFromHydraNLDatabase
from repo_utils.utils import repository_root_path
import os


def test_action_import_hrd_locations_from_hydranl_db(tmp_path):
    state = State(file_dir=tmp_path)
    repo_root = repository_root_path()
    state.question_answer.store(
        question_label="dir_hydranl_db",
        answer=os.path.join(repo_root, "tests", "systeem_testen", "224", "hrd_files"))
    action = ActionImportHRDLocationsFromHydraNLDatabase(state=state)
    action.execute()
    assert state.gdf.hrd_locations is not None
    assert state.gdf.hrd_locations.__len__() == 400
