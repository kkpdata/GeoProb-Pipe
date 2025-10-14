from pandas import DataFrame, concat
from typing import Optional, Dict, Union, List


class BColors:
    """ Helper object om prints kleur te geven. Gebruik als

    >>> print(BColors.WARNING, 'Mijn waarschuwing. ', BColors.ENDC)

    Let op. Met `BColors.ENDC` eindig je de kleur. Als je dit vergeet dan zijn alle volgende prints eveneens in kleur.

    """
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

    def __init__(self, about: str = ""):
        self.about: str = about
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
        new_rows = {
            "about": [self.about] * msgs.__len__(),
            "type": ["warning"] * msgs.__len__(),
            "msg": msgs,
        }
        self._append_new_rows(new_rows)

    def add_error(self, msg: Union[str, List[str]]):
        msgs = self._to_list(msg=msg)
        new_rows = {
            "about": [self.about] * msgs.__len__(),
            "type": ["error"] * msgs.__len__(),
            "msg": msgs,
        }
        self._append_new_rows(new_rows)

    def add_info(self, msg: Union[str, List[str]]):
        msgs = self._to_list(msg=msg)
        new_rows = {
            "about": [self.about] * msgs.__len__(),
            "type": ["info"] * msgs.__len__(),
            "msg": msgs,
        }
        self._append_new_rows(new_rows)

    def concat_with_df(self, df_to_append_to: Optional[DataFrame] = None) -> Optional[DataFrame]:
        """ Helper function to concatenate the validation messages with validation messages of another
        ValidationMessages-dataframe. """

        if self.df is None:
            return df_to_append_to

        if df_to_append_to is None:
            return self.df

        return concat([df_to_append_to, self.df])
