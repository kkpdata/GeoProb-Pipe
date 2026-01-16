from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional, List, cast
import scipy.stats as stats  # importeer de scipy.stats module
from geoprob_pipe.results.assemblage.functions import window_collect


@dataclass
class KansElement:
    pof: Optional[float] = None  # Faalkans van het element per jaar
    beta: Optional[float] = None  # Betrouwbaarheidindex van het element

    def __post_init__(self):
        if self.pof is not None:
            if not (0.0 <= self.pof <= 1.0):
                raise ValueError("pof moet tussen 0.0 en 1.0 liggen.")

        if self.beta is not None:
            if not math.isfinite(self.beta):
                raise ValueError("beta moet een eindige waarde zijn.")
            if (-38.0 <= self.beta <= 38.0) is False:
                raise ValueError("beta moet tussen -38.0 en 38.0 liggen.")

        if self.pof is None and self.beta is not None:
            self.pof = float(stats.norm.cdf(-1.0 * self.beta))

        if self.beta is None and self.pof is not None:
            self.beta = -1.0 * float(stats.norm.ppf(self.pof))


@dataclass
class UittredepuntElement(KansElement):
    M_value: Optional[float] = None


@dataclass
class VakElement:
    id: int
    M_van: float  # Locatie van het begin van het element [meters]
    M_tot: float  # Locatie van het einde van het element [meters]
    a: float  # Deel van het vak waarvoor de opschaalfactor wordt berekend (0-1)
    dL: float  # Equivalente, onafhankelijke lengte
    list_dsn: List[UittredepuntElement]  # Doorsnedekansen van het element per jaar
    invloedsfactor_belasting: float = 0.5  # Invloedsfactor van de belasting

    @property
    def L(self) -> float:
        return abs(self.M_tot - self.M_van)

    @property
    def N_vak(self) -> float:
        from geoprob_pipe.results.assemblage.functions import bepaal_N_vak
        return bepaal_N_vak(self.L, self.a, self.dL)

    # vak: max van dsn met Nvak
    @property
    def Pf_max_dsn(self) -> KansElement:
        list_pof = [cast(float, dsn.pof) for dsn in self.list_dsn]
        Pf_dsns = max(list_pof)
        Pf_vak = self.N_vak * Pf_dsns
        return KansElement(pof=Pf_vak)

    # vak: moving window met variable grootes
    @property
    def Pf_window_50m(self) -> KansElement:
        window_size = 50.0
        Pf_vak = window_collect(window_size, self.list_dsn,
                                self.M_van, self.M_tot)
        return KansElement(pof=Pf_vak)

    @property
    def Pf_window_100m(self) -> KansElement:
        window_size = 100.0
        Pf_vak = window_collect(window_size, self.list_dsn,
                                self.M_van, self.M_tot)
        return KansElement(pof=Pf_vak)

    @property
    def Pf_window_250m(self) -> KansElement:
        window_size = 250.0
        Pf_vak = window_collect(window_size, self.list_dsn,
                                self.M_van, self.M_tot)
        return KansElement(pof=Pf_vak)
    @property
    def Pf_window_500m(self) -> KansElement:
        window_size = 500.0
        Pf_vak = window_collect(window_size, self.list_dsn,
                                self.M_van, self.M_tot)
        return KansElement(pof=Pf_vak)
