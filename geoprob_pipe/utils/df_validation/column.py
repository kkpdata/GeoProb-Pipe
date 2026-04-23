from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.utils.df_validation import ValidationRequirement


class ColumnValidation:

    def __init__(self, column_name: str, requirements: List[ValidationRequirement]):
        self.column_name = column_name
        self.requirements = requirements
