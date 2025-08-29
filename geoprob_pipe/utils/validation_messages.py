from pandas import DataFrame, concat
from typing import Optional, Dict, Union, List


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ValidationMessages:

    def __init__(self):
        self.df: Optional[DataFrame] = None

    def _append_new_rows(self, new_rows: Dict):
        if self.df is None:
            self.df = DataFrame(new_rows)
        self.df = concat([self.df, DataFrame(new_rows)])

    @staticmethod
    def _to_list(msg: Union[str, List[str]]):
        assert isinstance(msg, (str, List))
        if isinstance(msg, str):
            msg = [msg]
        return msg

    @property
    def cnt(self) -> int:
        if self.df is None:
            return 0
        return self.df.__len__()

    def add_warning(self, msg: Union[str, List[str]]):
        msgs = self._to_list(msg=msg)
        new_rows = {"type": ["warning"] * msgs.__len__(), "msg": msgs}
        self._append_new_rows(new_rows)

    def add_error(self, msg: Union[str, List[str]]):
        msgs = self._to_list(msg=msg)
        new_rows = {"type": ["error"] * msgs.__len__(), "msg": msgs}
        self._append_new_rows(new_rows)

    def add_info(self, msg: Union[str, List[str]]):
        msgs = self._to_list(msg=msg)
        new_rows = {"type": ["info"] * msgs.__len__(), "msg": msgs}
        self._append_new_rows(new_rows)
