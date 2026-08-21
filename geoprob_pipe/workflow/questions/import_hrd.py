from geoprob_pipe.workflow.base_objects import Question, ValidationResult
from typing import Optional
from InquirerPy import inquirer


CHOICES = [
    "Hydra-NL database",
    "Ander GeoProb-Pipe bestand",
    "Nee",
]


class QuestionImportHRD(Question):
    question_label = "import_hrd"

    def ask(self) -> str:
        return inquirer.select(
            message="Wil je overschrijdingsfrequentielijnen importeren? En zo ja, uit welke bron? "
                    "Je kunt op een later moment handmatig overschrijdingsfrequentielijnen toevoegen aan het "
                    "bestand met invoer-Excel.",
            choices=CHOICES,
            default=CHOICES[0],
        ).execute()

    def validate(self, answer):
        if answer not in CHOICES:
            return ValidationResult(False, f"Kies één van de volgende opties: {CHOICES}.")
        return ValidationResult(True)

    @property
    def completed(self) -> bool:
        import_hrd: Optional[str] = self.state.retrieve_question_answer(self.question_label)
        if import_hrd is None or import_hrd == CHOICES[2]:
            return False
        return True
