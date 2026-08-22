from geoprob_pipe.workflow import State
from geoprob_pipe.workflow.actions import ActionImportHRDLocationsFromHydraNLDatabase


def test_action_import_hrd_locations_from_hydranl_db(tmp_path):
    state = State(file_dir=tmp_path)
    state.question_answer.store(
        question_label="dir_hydranl_db",
        answer=r"C:\Users\CP\Downloads\issue_invoer_wshd\alpha_versie_vincent\WBI2017_Benedenrijn_21-2_v04")
    action = ActionImportHRDLocationsFromHydraNLDatabase(state=state)
    action.execute()
    assert state.gdf.hrd_locations is not None
    assert state.gdf.hrd_locations.__len__() == 400
