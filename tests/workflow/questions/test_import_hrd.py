

def test_question_import_hrd():
    from geoprob_pipe.workflow.questions import QuestionImportHRD
    from geoprob_pipe.workflow.questions.import_hrd import CHOICES
    import numpy as np

    test_answers = CHOICES.copy()  # Force copy, otherwise you change CHOICES with .extend() on the next line.
    test_answers.extend(["Ja", None, 1, np.nan])
    test_results = [True, True, True, False, False, False, False]
    for test_answer, test_result in zip(test_answers, test_results):
        assert QuestionImportHRD.validate(answer=test_answer).is_valid == test_result, \
            f"Failed on {test_answer}, expected {test_result}."
