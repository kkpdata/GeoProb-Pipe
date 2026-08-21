from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass
if TYPE_CHECKING:
    from geoprob_pipe.workflow.state import State


class Step(ABC):

    def __init__(self, state: State):
        self.state = state

    @property
    @abstractmethod
    def completed(self) -> bool:
        """ Return True if the is already completed. Otherwise, step must be run. """
        raise NotImplementedError()

    @abstractmethod
    def execute(self):
        raise NotImplementedError()


@dataclass
class ValidationResult:
    is_valid: bool
    message: str | None = None


class Question(Step):
    question_label: str = None

    @abstractmethod
    def ask(self):
        raise NotImplementedError()

    def execute(self):
        answer = self.ask_until_valid()
        self.state.store_question_answer(question_label=self.question_label, answer=answer)

    @abstractmethod
    def validate(self, answer) -> ValidationResult:
        raise NotImplementedError()

    def ask_until_valid(self):
        while True:
            answer = self.ask()
            result = self.validate(answer)
            if result.is_valid:
                return answer


class Action(Step):

    @abstractmethod
    def execute(self):
        raise NotImplementedError()
