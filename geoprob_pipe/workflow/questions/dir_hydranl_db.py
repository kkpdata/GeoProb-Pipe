from geoprob_pipe.workflow.base_objects import Question, ValidationResult
from typing import Optional
from InquirerPy import inquirer
import os


def _folder_contains_hrd_db(hrd_dir: str) -> bool:
    cnt_sql_files = 0
    cnt_config_files = 0
    cnt_hlcd_files = 0

    for file in os.listdir(hrd_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".sqlite"):
            cnt_sql_files += 1
        if filename.endswith(".config.sqlite"):
            cnt_config_files += 1
        if filename.endswith("hlcd.sqlite"):
            cnt_hlcd_files += 1

    if cnt_sql_files == 3 and cnt_config_files == 1 and cnt_hlcd_files == 1:
        return True
    return False

class QuestionDirHydraNLDatabase(Question):
    label = "dir_hydranl_db"

    def ask(self) -> str:
        return inquirer.text(
            message="Specificeer het volledige pad naar de bestandsmap met de Hydra-NL database. "
                    "Dat zijn de hlcd, config en het database .sqlite-bestand zelf.",
        ).execute()

    @staticmethod
    def validate(answer) -> ValidationResult:
        manipulated_answer = answer.replace('"', '')
        if not os.path.isdir(manipulated_answer):
            return ValidationResult(False, "The provided path is not a directory.")
        if not _folder_contains_hrd_db(hrd_dir=manipulated_answer):
            return ValidationResult(
                False, "The provided directory does not contain the necessary Hydra-NL database-files.")
        # TODO: Validate HRD-point locations are valid
        return ValidationResult(True, manipulated_answer=manipulated_answer)

    @property
    def should_run(self) -> bool:
        answer: Optional[str] = self.state.question_answer.retrieve("import_hrd")
        if answer != "Hydra-NL database":
            return False
        return True

    @property
    def completed(self) -> bool:
        answer: Optional[str] = self.state.question_answer.retrieve(self.label)
        if answer is None:
            return False
        return True


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
