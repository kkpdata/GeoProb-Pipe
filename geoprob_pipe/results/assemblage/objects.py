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
    """DataClass voor het opslaan van de faalkans pf en de
    betrouwbaarheidsindex beta. Een van deze twee parameters is nodig om deze
    class te initialiseren.

    :raises ValueError: Als de pf niet tussen de 0 en de 1 ligt.
    :raises ValueError: Als beta geen eindige waarde heeft.
    :raises ValueError: Als beta groter is dan 38 of kleiner dan -38.
    """
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
class UittredepuntElement:
    """DataClass om alle relevante data van een uittredepunt te verzamelen.
    """
    m_value: float
    a: float
    converged: bool
    flow_chart_number: int
    advise: str
    pf: Optional[float] = None
    beta: Optional[float] = None

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
class VakElement:
    """ DataClass om alle relevante data van een vak te verzamelen.
    Vanuit deze class kunnen de verschillende methoden om tot een faalkans van
    het vak worden bepaald.
    """
    id: int
    m_van: float  # Locatie van het begin van het element [meters]
    m_tot: float  # Locatie van het einde van het element [meters]
    a: float
    delta_length: float  # Equivalente, onafhankelijke lengte
    dsn_list: List[UittredepuntElement]  # Doorsnede kansen van het element per jaar

    @property
    def length(self) -> float:
        return abs(self.m_tot - self.m_van)

    # noinspection PyPep8Naming
    @property
    def N_vak(self) -> float:
        return bepaal_N_vak(self.length, self.a, self.delta_length)

    @property
    def advise(self):
        if self.flow_chart_number == 21:
            return "Consider fine tuning on scenario-level."
        else:
            return "-"

    @property
    def flow_chart_number(self) -> int:
        fcn_list = [p.flow_chart_number for p in self.dsn_list]
        if fcn_list.__len__() == 0:
            return 0
        if min(fcn_list) == 11:
            return 21
        else:
            return 22

    # vak: Max van dsn met N_vak
    @property
    def pf_max_dsn(self) -> Tuple[KansElement, KansElement]:
        list_pf = [cast(float, dsn.pf) for dsn in self.dsn_list]
        if list_pf.__len__() > 0:
            pf_dsn = max(list_pf)
        else:
            pf_dsn = 0.0
        pf_vak = self.N_vak * pf_dsn

        return KansElement(pf=pf_dsn), KansElement(pf=pf_vak)

    @property
    def conv_max_dsn(self) -> bool:
        list_conv = [cast(bool, dsn.converged) for dsn in self.dsn_list]
        if False in list_conv:
            return False
        return True

    def pf_window(self, window_size: float):
        pf_sum, pf_max, window_elements = window_collect(
            window_size=window_size, point_list=self.dsn_list,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=self.id
            )
        """Helper om de `window_collect` functie op te zetten voor alle
        attributen.
        """
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    # # vak: moving window met variable lengtes
    # @property
    # def pf_window_50m(self) -> Tuple[KansElement, KansElement,
    #                                  List[WindowElement]]:
    #     return self._window_collect(50.0)
    #
    # @property
    # def pf_window_100m(self) -> Tuple[KansElement, KansElement,
    #                                   List[WindowElement]]:
    #     return self._window_collect(100.0)
    #
    # @property
    # def pf_window_200m(self) -> Tuple[KansElement, KansElement,
    #                                   List[WindowElement]]:
    #     return self._window_collect(200.0)
    #
    # @property
    # def pf_window_300m(self) -> Tuple[KansElement, KansElement,
    #                                   List[WindowElement]]:
    #     return self._window_collect(300.0)

    # vak: som van verschaalde dsn
    @property
    def pf_scaled(self) -> Tuple[KansElement, KansElement,
                                 List[WindowElement]]:
        pf_sum, pf_max, window_elements = scaled_collect(
            self.delta_length, self.dsn_list, self.m_van,
            self.m_tot, vak_id=self.id
        )
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements


@dataclass
class WindowElement:
    """DataClass voor het verzamelen va alle data uit een window dat wordt
    opgezet in `window_collect` of `scaled_collect`.

    :raises AttributeError: Als een attribute wordt opgevraagd dat niet is
        toegevoegd.
    """

    m_van: float  # Begin punt in meters
    m_tot: float  # Eindpunt in meters
    window_size: float  # Groote van de window
    window_id: int  # Id nummer toegewezen aan window
    pf: float  # Faalkans toegewezen aan window
    flow_chart_number: int
    advise: str
    _vak_id: Optional[int] = None
    _a: Optional[float] = None
    _m_uittredepunt: Optional[float] = None
    _n_vak: Optional[float] = None

    @property
    def length(self):
        return self.m_tot - self.m_van

    @property
    def kans_dsn(self) -> KansElement:
        return KansElement(pf=self.pf)

    @property
    def a(self) -> float:
        if self._a:
            return cast(float, self._a)
        else:
            raise AttributeError("No attribute a specified in object.")

    @property
    def vak_id(self) -> int:
        if isinstance(self._vak_id, int):
            return cast(int, self._vak_id)
        else:
            raise AttributeError("No attribute vak_id specified in object.")

    @property
    def m_uittredepunt(self) -> float:
        if isinstance(self._m_uittredepunt, float):
            return self._m_uittredepunt
        else:
            raise AttributeError(
                "No attribute m_uittredepunt specified in object."
                )

    @property
    def n_vak(self) -> float:
        if isinstance(self._n_vak, float):
            return self._n_vak
        else:
            raise AttributeError(
                "No attribute N_vak specified in object."
                )


@dataclass
class TrajectElement:
    """DataClass om de data van het traject te verzamelen.
    """
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

    def pf_window(self, window_size: float) -> Tuple[KansElement, KansElement, List[WindowElement]]:
        pf_sum, pf_max, window_elements = window_collect(
            window_size=window_size, point_list=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None
            )
        """Helper om de `window_collect` functie op te zetten voor alle
        attributen.
        """
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements

    # # traject: moving window met variable lengtes
    # @property
    # def pf_window_50m(self) -> Tuple[KansElement, KansElement,
    #                                  List[WindowElement]]:
    #     return self._window_collect(50.0)
    #
    # @property
    # def pf_window_100m(self) -> Tuple[KansElement, KansElement, List[WindowElement]]:
    #     return self._window_collect(100.0)
    #
    # @property
    # def pf_window_200m(self) -> Tuple[KansElement, KansElement,
    #                                   List[WindowElement]]:
    #     return self._window_collect(200.0)
    #
    # @property
    # def pf_window_300m(self) -> Tuple[KansElement, KansElement,
    #                                   List[WindowElement]]:
    #     return self._window_collect(300.0)

    # traject: som van verschaalde dsn
    @property
    def pf_scaled(self) -> Tuple[KansElement, KansElement,
                                 List[WindowElement]]:
        pf_sum, pf_max, window_elements = scaled_collect(
            dL=self.delta_length, point_list=self.list_dsn,
            m_van=self.m_van, m_tot=self.m_tot, vak_id=None)
        return KansElement(pf=pf_sum), KansElement(pf=pf_max), window_elements
