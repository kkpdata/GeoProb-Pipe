import math
from dataclasses import dataclass
from typing import Tuple
from geoprob_pipe.calculations.physical_components.geohydro_functions import calc_lambda, calc_r_BIT, calc_r_BUT, calc_W


@dataclass
class Model4a:
    """Class for groundwater model 4A Technisch Rapport Waterspanningen bij Dijken"""

    kD: float
    D: float
    c1: float
    c3: float
    L1: float
    L3: float
    x_but: float
    x_bit: float

    # noinspection PyPep8Naming
    @property
    def L2(self) -> float:
        return abs(self.x_bit - self.x_but)

    @property
    def lambda1(self) -> float:
        return calc_lambda(self.kD, self.c1)

    @property
    def lambda3(self) -> float:
        return calc_lambda(self.kD, self.c3)

    # noinspection PyPep8Naming
    @property
    def W1(self) -> float:
        return calc_W(self.lambda1, self.L1)

    # noinspection PyPep8Naming
    @property
    def W3(self) -> float:
        return calc_W(self.lambda3, self.L3)

    # noinspection PyPep8Naming
    @property
    def W_rad(self) -> float:
        return 0.44 * self.D

    # noinspection PyPep8Naming
    @property
    def W_tot4a(self) -> float:
        return self.W1 + self.L2 + self.W3

    # noinspection PyPep8Naming
    @property
    def r_BUT(self) -> float:
        return calc_r_BUT(self.W1, self.L2, self.W3)

    # noinspection PyPep8Naming
    @property
    def r_BIT(self) -> float:
        return calc_r_BIT(self.W1, self.L2, self.W3)

    def respons(self, x: float) -> Tuple[float, float, float]:
        """calculate response at x given model
        x positive direction is inwards, so x_but < x_bit"""

        # Before floodplain
        if x < self.x_but - self.L1:
            r = 1.0

        # Floodplain
        elif self.x_but > x >= self.x_but - self.L1:
            r = 1.0 - (1.0 - self.r_BUT) * math.sinh(
                (self.L1 + x - self.x_but) / self.lambda1
            ) / math.sinh(self.L1 / self.lambda1)

        # Hinterland (where potential is affected)
        elif self.x_bit < x <= self.x_bit + self.L3:
            r = (
                self.r_BIT
                * math.sinh((self.L3 - x + self.x_bit) / self.lambda3)
                / math.sinh(self.L3 / self.lambda3)
            )

        #
        elif x > self.x_bit + self.L3:
            r = 0.0

        # dike
        else:
            r = self.r_BIT + (self.r_BUT - self.r_BIT) * (self.x_bit - x) / (
                self.x_bit - self.x_but
            )

        return r, self.r_BUT, self.r_BIT