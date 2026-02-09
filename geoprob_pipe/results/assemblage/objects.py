from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional, List, Tuple, cast
from geoprob_pipe.results.assemblage.functions import bepaal_N_vak
import scipy.stats as stats  # importeer de scipy.stats module
from geoprob_pipe.results.assemblage.functions import (
    combine_series, window_collect, scaled_collect)


@dataclass
class KansElement:
    pf: Optional[float] = None  # Probability of failure, Faalkans van het element per jaar
    beta: Optional[float] = None  # Betrouwbaarheidsindex van het element

    def __post_init__(self):

        if self.pf is not None:
            if not (0.0 <= self.pf <= 1.0):
                raise ValueError("pof moet tussen 0.0 en 1.0 liggen.")

        if self.beta is not None:
            if not math.isfinite(self.beta):
                raise ValueError("beta moet een eindige waarde zijn.")
            if (-38.0 <= self.beta <= 38.0) is False:
                raise ValueError("beta moet tussen -38.0 en 38.0 liggen.")

        if self.pf is None and self.beta is not None:
            self.pf = float(stats.norm.cdf(-1.0 * self.beta))

        if self.beta is None and self.pf is not None:
            self.beta = -1.0 * float(stats.norm.ppf(self.pf))


@dataclass
class UittredepuntElement(KansElement):
    m_value: Optional[float] = None
    a: Optional[float] = None
    converged: Optional[bool] = None


@dataclass
class VakElement:
    id: int
    m_van: float  # Locatie van het begin van het element [meters]
    m_tot: float  # Locatie van het einde van het element [meters]
    a: float
    delta_length: float  # Equivalente, onafhankelijke lengte
    list_dsn: List[UittredepuntElement]  # Doorsnede kansen van het element per jaar

    @property
    def length(self) -> float:
        return abs(self.m_tot - self.m_van)

    @property
    def N_vak(self) -> float:
        return bepaal_N_vak(self.length, self.a, self.delta_length)

    # vak: Max van dsn met N_vak
    @property
    def pf_max_dsn(self) -> Tuple[KansElement, KansElement]:
        list_pf = [cast(float, dsn.pf) for dsn in self.list_dsn]
        if list_pf.__len__() > 0:
            pf_dsn = max(list_pf)
        else:
            pf_dsn = 0.0
        pf_vak = self.N_vak * pf_dsn

        return KansElement(pf=pf_dsn), KansElement(pf=pf_vak)

    @property
    def conv_max_dsn(self) -> bool:
        list_conv = [cast(bool, dsn.converged) for dsn in self.list_dsn]
        if False in list_conv:
            return False
        return True

    # vak: moving window met variable lengtes
    @property
    def pf_window_50m(self) -> Tuple[KansElement, KansElement,
                                     List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=50.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=self.id
            )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_100m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=100.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=self.id
            )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_200m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=200.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=self.id
            )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_300m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=300.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=self.id
            )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    # vak: som van verschaalde dsn
    @property
    def pf_scaled(self) -> Tuple[KansElement, KansElement]:
        pf_sum, pf_max = scaled_collect(
            self.delta_length, self.list_dsn, self.m_van, self.m_tot
        )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max)


@dataclass
class WindowElement:
    m_van: float
    m_tot: float
    window_size: float
    vak_id: Optional[int]
    window_id: int
    pf: float

    @property
    def length(self):
        return self.m_tot - self.m_van

    @property
    def kans_dsn(self) -> KansElement:
        return KansElement(pf=self.pf)


@dataclass
class TrajectElement:
    list_vakken: list[VakElement]
    list_dsn: list[UittredepuntElement]
    delta_length: float

    @property
    def m_van(self) -> float:
        list_m_van = []
        for vak in self.list_vakken:
            m_van = vak.m_van
            list_m_van.append(m_van)
        return min(list_m_van)

    @property
    def m_tot(self) -> float:
        list_m_tot = []
        for vak in self.list_vakken:
            m_van = vak.m_tot
            list_m_tot.append(m_van)
        return max(list_m_tot)

    # traject: som van vakken
    @property
    def pf_max_vak(self) -> Tuple[KansElement, KansElement]:
        pfs: list[float] = []
        for vak in self.list_vakken:
            pf = cast(float, vak.pf_max_dsn[0].pf)
            pfs.append(pf)
        pf_sum, pf_max = combine_series(pfs)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max)

    # traject: moving window met variable lengtes
    @property
    def pf_window_50m(self) -> Tuple[KansElement, KansElement,
                                     List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=50.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_100m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=100.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_200m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=200.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    @property
    def pf_window_300m(self) -> Tuple[KansElement, KansElement,
                                      List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=300.0, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    # traject: som van verschaalde dsn
    @property
    def pf_scaled(self) -> Tuple[KansElement, KansElement]:
        pf_sum, pf_max = scaled_collect(
            dL=self.delta_length, list_dsn=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max)
