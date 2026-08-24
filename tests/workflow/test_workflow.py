import os.path

from geoprob_pipe.workflow import State, steps
from geoprob_pipe.workflow.questions import QuestionDirHydraNLDatabase, QuestionImportHRD
from geoprob_pipe.workflow.questions.import_hrd import CHOICES
from geoprob_pipe.workflow.base_objects import Question
from repo_utils.utils import repository_root_path
import random


# GeoProb-Pipe/tests/systeem_testen/224/hrd_files


def test_workflow(tmp_path):
    repo_root = repository_root_path()
    valid_answers = {
        QuestionImportHRD.label: CHOICES,
        QuestionDirHydraNLDatabase.label: [os.path.join(repo_root, "tests", "systeem_testen", "224", "hrd_files")],
    }
    # TODO: Hoe specificeer ik een relatief pad wat werkt in Ubuntu GitHub en lokaal bij ons.
    # TODO: Sowieso test bestanden opzetten en kijken of ik nog ergens lokale paden gebruik.

    state = State(file_dir=tmp_path)
    for obj in steps:
        step = obj(state=state)
        print(f"\n{step.label}: {step.should_run=} {step.completed=}")

        # Check
        if not step.should_run:
            continue
        if step.completed:
            continue

        # Fake 'execute' question
        if issubclass(obj, Question):
            answer = random.choice(valid_answers[obj.label])
            print(f"Now popping '{answer}' to '{obj.label}'.")
            state.question_answer.store(question_label=obj.label, answer=answer)
            assert step.completed == True
            continue

        # Thus Action
        step.execute()
