from geoprob_pipe.workflow.base_objects import Question, ValidationResult
from typing import Optional
from InquirerPy import inquirer


CHOICES = [
    "Hydra-NL database",
    "Ander GeoProb-Pipe bestand",
    "Nee",
]


class QuestionImportHRD(Question):
    label = "import_hrd"

    def ask(self) -> str:
        return inquirer.select(
            message="Wil je overschrijdingsfrequentielijnen importeren? En zo ja, uit welke bron? "
                    "Je kunt op een later moment handmatig overschrijdingsfrequentielijnen toevoegen aan het "
                    "bestand met invoer-Excel.",
            choices=CHOICES,
            default=CHOICES[0],
        ).execute()

    @staticmethod
    def validate(answer):
        if answer not in CHOICES:
            return ValidationResult(False, f"Kies één van de volgende opties: {CHOICES}.")
        return ValidationResult(True)

    @property
    def should_run(self) -> bool:
        return True  # Always ask if HRD-data should be imported.

    @property
    def completed(self) -> bool:
        answer: Optional[str] = self.state.retrieve_question_answer(self.label)
        if answer is None or answer == CHOICES[2]:
            return False
        return True
