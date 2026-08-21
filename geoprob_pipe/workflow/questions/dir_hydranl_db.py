from geoprob_pipe.workflow.base_objects import Question, ValidationResult
from typing import Optional
from InquirerPy import inquirer
import os


class QuestionDirHydraNLDatabase(Question):
    label = "dir_hydranl_db"

    def ask(self) -> str:
        return inquirer.text(
            message="Specificeer het volledige pad naar de bestandsmap met de Hydra-NL database. "
                    "Dat zijn de hlcd, config en het database .sqlite-bestand zelf.",
        ).execute()

    def validate(self, answer) -> ValidationResult:
        manipulated_answer = answer.replace('"', '')
        if not os.path.isdir(manipulated_answer):
            return ValidationResult(False, "The provided path is not a directory.")
        # TODO: Validate contains correct files in dir
        # TODO: Validate HRD-point locations are valid
        return ValidationResult(True, manipulated_answer=manipulated_answer)

    @property
    def should_run(self) -> bool:
        answer: Optional[str] = self.state.retrieve_question_answer("import_hrd")
        if answer != "Hydra-NL database":
            return False
        return True

    @property
    def completed(self) -> bool:
        answer: Optional[str] = self.state.retrieve_question_answer(self.label)
        if answer is None:
            return False
        return True
