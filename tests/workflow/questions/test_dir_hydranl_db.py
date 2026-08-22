from geoprob_pipe.workflow.questions import QuestionDirHydraNLDatabase


def test_question_dir_hydra_nl_database():
    test_answers = [
        r"C:\Users\CP\Downloads\false_fix\Analyse16-2_V3.2.geoprob_pipe.gpkg",
        r"C:\Users\CP\Downloads\false_fix\exports",
        r"C:\Users\CP\Downloads\issue_invoer_wshd\alpha_versie_vincent\WBI2017_Benedenrijn_21-2_v04",
    ]
    test_results = [
        False,
        False,
        True,
    ]
    for test_answer, test_result in zip(test_answers, test_results):
        assert QuestionDirHydraNLDatabase.validate(answer=test_answer).is_valid == test_result
