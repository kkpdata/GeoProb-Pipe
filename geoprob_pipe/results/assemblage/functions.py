from __future__ import annotations
import numpy as np
import pandas as pd
from operator import attrgetter
from decimal import Decimal, getcontext
from typing import TYPE_CHECKING, cast, Tuple, List, Optional
if TYPE_CHECKING:
    from geoprob_pipe.results.assemblage.objects import (
        UittredepuntElement, WindowElement)


def combine_series(list_pf: list[float]) -> Tuple[float, float]:
    getcontext().prec = 30
    if list_pf.__len__() > 0:
        inv_pf = Decimal(1)
        for pf in list_pf:
            inv_pf = inv_pf * Decimal(1) - Decimal.from_float(pf)
        return float(Decimal(1) - inv_pf), max(list_pf)
    else:
        return 0.0, 0.0


def bepaal_N_vak(L: float, a: float, dL: float) -> float:
    if a < 0:
        raise ValueError("a moet groter zijn dan 0.")

    if L < 0 or dL < 0:
        raise ValueError("De lengte L en dL moeten groter zijn dan 0.")

    N_vak = max(1.00, (a * L) / dL)
    return N_vak


def window_collect(window_size: float, list_dsn: list[UittredepuntElement],
                   m_van: float, m_tot: float, vak_id: Optional[int] = None
                   ) -> tuple[float, float, List[WindowElement]]:
    from geoprob_pipe.results.assemblage.objects import WindowElement
    list_m_value: List[float] = cast(
        List[float], [dsn.m_value for dsn in list_dsn]
        )
    if list_m_value.__len__() == 0:
        return 0.0, 0.0, []

    list_pf = [dsn.pf for dsn in list_dsn]

    df_vak = pd.DataFrame({
            "M_value": list_m_value,
            "pf": list_pf
        })

    bins_window = np.arange(
        m_van, m_tot, window_size
        ).tolist()
    bins_window.append(m_tot)

    bin_cat: pd.Categorical = cast(pd.Categorical, pd.cut(
        list_m_value,
        bins=bins_window,
        right=False,
        include_lowest=True
        ))
    df_vak = df_vak.assign(bin=bin_cat)
    df_bin = (df_vak.groupby("bin", observed=False)["pf"].max()
              .reindex(bin_cat.categories).fillna(0))

    sum_pf, max_pf = combine_series(df_bin.to_list())
    window_elements: List[WindowElement] = []
    bins_window.append(m_tot)  # add end of final window
    for i in range(len(bins_window)-2):
        window_elements.append(WindowElement(
            m_van=bins_window[i],
            m_tot=bins_window[i+1],
            window_size=window_size,
            window_id=i,
            pf=df_bin[df_bin.index[i]],
            _vak_id=vak_id,
        ))
    return sum_pf, max_pf, window_elements


def scaled_collect(
        dL: float, list_dsn: list[UittredepuntElement],
        m_van: float, m_tot: float, vak_id: Optional[int] = None
        ) -> tuple[float, float, List[WindowElement]]:
    from geoprob_pipe.results.assemblage.objects import WindowElement
    if list_dsn.__len__() == 0:
        return 0.0, 0.0, []

    list_dsn.sort(key=attrgetter("m_value"))
    clusters: List[List[UittredepuntElement]] = []
    current_cluster: List[UittredepuntElement] = [list_dsn[0]]
    cluster_start: float = list_dsn[0].m_value

    for dsn in list_dsn[1:]:
        if dsn.m_value - cluster_start <= 5.0:
            current_cluster.append(dsn)
        else:
            clusters.append(current_cluster)
            current_cluster = [dsn]
            cluster_start = dsn.m_value
    clusters.append(current_cluster)

    selected = [max(cluster, key=lambda x: cast(float, x.pf))
                for cluster in clusters]
    pfs: List[float] = []
    window_elements: List[WindowElement] = []

    for i, sel in enumerate(selected):
        cluster_start = max(
            m_van, sel.m_value - (sel.m_value - clusters[i][0].m_value)
            )
        if i == 0:
            seg_start = m_van
        else:
            seg_start = (
                clusters[i-1][-1].m_value
                + (clusters[i][0].m_value - clusters[i-1][-1].m_value)
                / 2)
        if i == len(selected)-1:
            seg_end = m_tot
        else:
            seg_end = (
                clusters[i][-1].m_value
                + (clusters[i+1][0].m_value - clusters[i][-1].m_value)
                / 2)

        length = seg_end - seg_start
        a = sel.a
        N_vak = bepaal_N_vak(length, a, dL)
        pf = cast(float, sel.pf) * N_vak
        pfs.append(pf)
        window_elements.append(
            WindowElement(
                m_van=seg_start,
                m_tot=seg_end,
                window_size=length,
                window_id=i,
                _vak_id=vak_id,
                pf=pf,
                _a=a,
                _m_uittredepunt=sel.m_value,
                _n_vak=N_vak
            )
        )
    sum_pf, max_pf = combine_series(pfs)
    return sum_pf, max_pf, window_elements
