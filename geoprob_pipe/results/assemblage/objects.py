from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional, List, cast
from geoprob_pipe.results.assemblage.functions import bepaal_N_vak
import scipy.stats as stats  # importeer de scipy.stats module
from geoprob_pipe.results.assemblage.functions import (
    corrected_sum, window_collect, scaled_collect)


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
    a: Optional[float] = None
    converged: Optional[bool] = None


@dataclass
class VakElement:
    id: int
    M_van: float  # Locatie van het begin van het element [meters]
    M_tot: float  # Locatie van het einde van het element [meters]
    a: float
    dL: float  # Equivalente, onafhankelijke lengte
    list_dsn: List[UittredepuntElement]  # Doorsnedekansen van het element per jaar
    invloedsfactor_belasting: float = 0.5  # Invloedsfactor van de belasting

    @property
    def L(self) -> float:
        return abs(self.M_tot - self.M_van)

    @property
    def N_vak(self) -> float:
        return bepaal_N_vak(self.L, self.a, self.dL)

    # vak: max van dsn met Nvak
    @property
    def Pf_max_dsn(self) -> KansElement:
        list_pof = [cast(float, dsn.pof) for dsn in self.list_dsn]
        if list_pof != []:
            Pf_dsns = max(list_pof)
        else:
            Pf_dsns = 0.0
        Pf_vak = self.N_vak * Pf_dsns
        return KansElement(pof=Pf_vak)

    @property
    def Conv_max_dsn(self) -> bool:
        list_conv = [cast(bool, dsn.converged) for dsn in self.list_dsn]
        if False in list_conv:
            return False
        return True

    # vak: moving window met variable grootes
    @property
    def Pf_window_50m(self) -> tuple[KansElement, KansElement]:
        Pf_vak = window_collect(window_size=50.0, list_dsn=self.list_dsn,
                                M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=Pf_vak[0]), KansElement(pof=Pf_vak[1])

    @property
    def Pf_window_100m(self) -> tuple[KansElement, KansElement]:
        Pf_vak = window_collect(window_size=100.0, list_dsn=self.list_dsn,
                                M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=Pf_vak[0]), KansElement(pof=Pf_vak[1])

    @property
    def Pf_window_200m(self) -> tuple[KansElement, KansElement]:
        Pf_vak = window_collect(window_size=200.0, list_dsn=self.list_dsn,
                                M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=Pf_vak[0]), KansElement(pof=Pf_vak[1])

    @property
    def Pf_window_300m(self) -> tuple[KansElement, KansElement]:
        Pf_vak = window_collect(window_size=300.0, list_dsn=self.list_dsn,
                                M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=Pf_vak[0]), KansElement(pof=Pf_vak[1])

    # vak: som van verschaalde dsn
    @property
    def Pf_scaled(self) -> tuple[KansElement, KansElement]:
        Pf_scaled = scaled_collect(
            self.dL, self.list_dsn, self.M_van, self.M_tot
        )
        return KansElement(pof=Pf_scaled[0]), KansElement(pof=Pf_scaled[1])


@dataclass
class TrajectElement():
    list_vakken: list[VakElement]
    list_dsn: list[UittredepuntElement]
    dL: float

    @property
    def M_van(self) -> float:
        list_m_van = []
        for vak in self.list_vakken:
            m_van = vak.M_van
            list_m_van.append(m_van)
        return min(list_m_van)

    @property
    def M_tot(self) -> float:
        list_m_tot = []
        for vak in self.list_vakken:
            m_van = vak.M_tot
            list_m_tot.append(m_van)
        return max(list_m_tot)

    # traject: som van vakken
    @property
    def Pf_max_vak(self) -> tuple[KansElement, KansElement]:
        pofs: list[float] = []
        for vak in self.list_vakken:
            pof = cast(float, vak.Pf_max_dsn.pof)
            pofs.append(pof)
        return KansElement(pof=corrected_sum(pofs)), KansElement(pof=max(pofs))

    # traject: moving window met variable groote
    @property
    def Pf_window_50m(self) -> tuple[KansElement, KansElement]:
        pof = window_collect(window_size=50.0, list_dsn=self.list_dsn,
                             M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=pof[0]), KansElement(pof=pof[1])

    @property
    def Pf_window_100m(self) -> tuple[KansElement, KansElement]:
        pof = window_collect(window_size=100.0, list_dsn=self.list_dsn,
                             M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=pof[0]), KansElement(pof=pof[1])

    @property
    def Pf_window_200m(self) -> tuple[KansElement, KansElement]:
        pof = window_collect(window_size=200.0, list_dsn=self.list_dsn,
                             M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=pof[0]), KansElement(pof=pof[1])

    @property
    def Pf_window_300m(self) -> tuple[KansElement, KansElement]:
        pof = window_collect(window_size=300.0, list_dsn=self.list_dsn,
                             M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=pof[0]), KansElement(pof=pof[1])

    # traject: som van verschaalde dsn
    @property
    def Pf_scaled(self) -> tuple[KansElement, KansElement]:
        pof = scaled_collect(dL=self.dL, list_dsn=self.list_dsn,
                             M_van=self.M_van, M_tot=self.M_tot)
        return KansElement(pof=pof[0]), KansElement(pof=pof[1])
