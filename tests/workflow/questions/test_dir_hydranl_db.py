


def test_question_dir_hydra_nl_database():
    ##
    from geoprob_pipe.workflow.questions import QuestionDirHydraNLDatabase
    from repo_utils.utils import find_repo_root
    import os
    repo_root = find_repo_root()
    test_answers = [
        os.path.join(repo_root, "tests", "systeem_testen", "224", "hrd_files", "WBI2017_Bovenrijn_224_v04.sqlite"),
        os.path.join(repo_root, "tests", "systeem_testen", "224"),
        os.path.join(repo_root, "tests", "systeem_testen", "224", "hrd_files"),
    ]
    test_results = [
        False,
        False,
        True,
    ]
    for test_answer, test_result in zip(test_answers, test_results):
        assert QuestionDirHydraNLDatabase.validate(answer=test_answer).is_valid == test_result
    ##