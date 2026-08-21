from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from geoprob_pipe.utils.validation_messages import BColors
from dataclasses import dataclass
if TYPE_CHECKING:
    from geoprob_pipe.workflow.state import State


class Step(ABC):
    label: str = None

    def __init__(self, state: State):
        self.state = state

    @property
    @abstractmethod
    def should_run(self) -> bool:
        """ Return True if this step should be run, based on the state of the project. """
        raise NotImplementedError()

    @property
    @abstractmethod
    def completed(self) -> bool:
        """ Return True if this step is already completed. Otherwise, step must be run. """
        raise NotImplementedError()

    @abstractmethod
    def execute(self):
        raise NotImplementedError()


@dataclass
class ValidationResult:
    is_valid: bool
    message: str | None = None
    manipulated_answer: str | None = None


class Question(Step):

    @abstractmethod
    def ask(self):
        raise NotImplementedError()

    def execute(self):
        answer = self.ask_until_valid()
        self.state.store_question_answer(question_label=self.label, answer=answer)

    @staticmethod
    @abstractmethod
    def validate(answer) -> ValidationResult:
        raise NotImplementedError()

    def ask_until_valid(self):
        while True:
            answer = self.ask()

            # Validate
            result: ValidationResult = self.validate(answer)
            if not result.is_valid:
                print(f"{BColors.WARNING}{result.message}{BColors.ENDC}")

            # Is valid
            if result.manipulated_answer:
                return result.manipulated_answer
            return answer


class Action(Step):

    @abstractmethod
    def execute(self):
        raise NotImplementedError()
