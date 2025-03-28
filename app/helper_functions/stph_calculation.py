import limitstatepiping_model4a as lm4a
from dataclasses import dataclass
from typing import List,Optional
import scipy.stats as sct

# Functions for calculation of characteristic values



@dataclass
class Stochast:
    """
    Class for stochastic variables
    """
    name: str
    mean: float
    std: Optional[float] = None
    vc: Optional[float] = None
    shift: Optional[float] = None
    dist: List[str] = ['normal', 'lognormal']
    unit: Optional[str] = None
    type_characteristic_value: List[str] = ['UL', 'LL']

    @property
    def characteristic(self, type: List["UL", "LL"]) -> float:
        """
        Berekent de karakteristieke waarde van de stochastische variabele
        """
        return lm4a.calc_characteristic_value(self.mean, self.std, self.vc, self.dist[0])

@dataclass
class StphCalculation:
    """"
    Class for semi-probabilistic calculation of piping
    """
