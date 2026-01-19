from __future__ import annotations
import numpy as np
import pandas as pd
from operator import attrgetter
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from geoprob_pipe.results.assemblage.objects import UittredepuntElement


def bepaal_N_vak(L: float, a: float, dL: float) -> float:
    r"""Bepaalt de opschaalfactor per vak.

    .. math::
        N_{vak} = max(1, \frac{a \cdot L}{\Delta L})

    Parameters
    ----------
    L : float
        De lengte van het vak [m]
    a : float
        deel van het vak waarvoor de opschaalfactor wordt berekend (0-1).
    dL : float
        equivalente onafhankelijke mechanismelengte [m].

    Returns
    -------
    float
        De opschaalfactor van het vak

    Raises
    ------
    ValueError
        Als a niet tussen 0 en 1 ligt, of als L en dL niet positief zijn.

    Examples
    --------
    >>> bepaal_N_vak(600.0, 1.0, 300.0)
    2.0
    >>> bepaal_N_vak(400.0, 0.5, 300.0)
    1.0
    """
    if a < 0:
        raise ValueError("a moet groter zijn dan 0.")

    if L < 0 or dL < 0:
        raise ValueError("De lengte L en dL moeten groter zijn dan 0.")

    N_vak = max(1, (a * L) / dL)
    return N_vak


def window_collect(window_size: float, list_dsn: list[UittredepuntElement],
                   M_van: float, M_tot: float) -> float:
    list_M_value = [dsn.M_value for dsn in list_dsn]
    list_pof = [dsn.pof for dsn in list_dsn]

    vak_df = pd.DataFrame({
            "M_value": list_M_value,
            "pof": list_pof
        })

    bins_window = np.arange(
        np.floor(M_van), np.ceil(M_tot), window_size
        )

    vak_df["bin"] = pd.cut(
        vak_df["M_value"],
        bins=bins_window,
        labels=False,
        right=False,
        include_lowest=True
        )

    bin_df = (
        vak_df.dropna(subset=["bin"])
        .groupby("bin")["pof"]
        .max()
        )
    return float(bin_df.sum())


def scaled_collect(dL: float,
                   list_dsn: list[UittredepuntElement],
                   M_van: float, M_tot: float) -> float:
    list_dsn.sort(key=attrgetter("M_value"))
    pofs = []
    for i in range(0, len(list_dsn)-1):
        if i == 1:
            L_van: float = M_van
        else:
            L_van: float = (cast(float, list_dsn[i-1].M_value)
                            + (cast(float, list_dsn[i].M_value)
                               - cast(float, list_dsn[i-1].M_value)) / 2)
        if i == len(list_dsn):
            L_tot: float = M_tot
        else:
            L_tot: float = (cast(float, list_dsn[i].M_value)
                            + (cast(float, list_dsn[i+1].M_value)
                               - cast(float, list_dsn[i].M_value)) / 2)
        # Absolute incase of reversed order in data of van en tot.
        L = abs(L_tot - L_van)
        a = cast(float, list_dsn[i].a)
        N_vak = bepaal_N_vak(L, a, dL)
        pof = cast(float, list_dsn[i].pof) * N_vak
        pofs.append(pof)
    return sum(pofs)
