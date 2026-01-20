from __future__ import annotations
import numpy as np
import pandas as pd
from operator import attrgetter
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from geoprob_pipe.results.assemblage.objects import UittredepuntElement


def corrected_sum(list_pof: list[float]) -> float:
    r"""Gecorrigeerde som van de faalkansen. De som van onafhankelijke
    faalkansen is geljk aan: 1 min het product van 1 min de inviduele
    faalkans.

    Parameters
    ----------
    list_pof : list[float]
        Lijst van de faalkans die opgeteld moeten worden.

    Returns
    -------
    float
        Gecorrigeerde som van de faalkansen.
    """
    if list_pof != []:
        corr_inv_pof = 1
        for pof in list_pof:
            corr_inv_pof = corr_inv_pof * (1.0 - pof)
        return 1.0 - corr_inv_pof
    else:
        return 0.0


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
                   M_van: float, M_tot: float) -> tuple[float, float]:
    """
    Agregeert faalkansen (`pof`) per M-venster en somt de bin-maxima op.

    De functie maakt vaste vensters (bins) over het domein van M-waarden met
    breedte `window_size` binnen het bereik ``[M_van, M_tot)``. Voor elk
    venster wordt de maximale waarde van `pof` bepaald uit de elementen die
    met hun `M_value` in dat venster vallen. De output is de som van
    deze venster-maxima.

    Parameters
    ----------
    window_size : float
        De breedte van elk M-venster (bin). Moet positief zijn en groter dan 0.
    list_dsn : list of UittredepuntElement
        Lijst met uittredepunten die minimaal de attributen bevatten:
        - ``M_value`` (float): de M-positie van het uittredepunt.
        - ``pof`` (float): probability of failure (faalkans) behorend bij
        het uittredepunt.
    M_van : float
        Ondergrens van het M-bereik. De bins starten bij ``floor(M_van)``.
    M_tot : float
        Bovengrens van het M-bereik (exclusief). De bins lopen tot
        ``ceil(M_tot)``, waarbij `pandas.cut` met ``right=False``
        half-open intervallen maakt ``[links, rechts)``.

    Returns
    -------
    float
        De som van de maximale `pof` per niet-lege bin over het bereik.
        Bins zonder waarnemingen dragen niet bij aan de som.
    """
    list_M_value = [dsn.M_value for dsn in list_dsn]
    list_pof = [dsn.pof for dsn in list_dsn]

    vak_df = pd.DataFrame({
            "M_value": list_M_value,
            "pof": list_pof
        })

    bins_window = np.arange(
        M_van, M_tot, window_size
        ).tolist()

    vak_df["bin"] = pd.cut(
        x=vak_df["M_value"],
        bins=bins_window,
        labels=False,
        right=False,
        include_lowest=True
        )

    bin_df: pd.Series[float] = (
        vak_df.dropna(subset=["bin"])
        .groupby("bin")["pof"]
        .max()
        )
    sum_pof = corrected_sum(bin_df.to_list())
    if bin_df.to_list() != []:
        max_pof = max(bin_df.to_list())
    else:
        max_pof = 0.0
    return sum_pof, max_pof


def scaled_collect(dL: float,
                   list_dsn: list[UittredepuntElement],
                   M_van: float, M_tot: float) -> tuple[float, float]:
    """
    Bepaald de totale faalkans door lokale pof-waarden te wegen
    met een lengtefactor per punt, afgeleid uit de midpoints tot buren.

    De lijst `list_dsn` wordt eerst gesorteerd op `M_value`. Voor elk punt
    wordt een lokale representatieve lengte L bepaald als de afstand tussen de
    halve afstand naar de vorige buur (L_van) en de halve afstand naar de
    volgende buur (L_tot). De lokale faalkans `pof` wordt vervolgens geschaald
    met een opschaalfactor `N_vak = bepaal_N_vak(L, a, dL)`, waarbij `a` per
    punt komt uit `dsn.a` en `dL` de equivalente onafhankelijke
    mechanismelengte is. De uitkomst is de som van `pof * N_vak` over
    alle punten.

    Parameters
    ----------
    dL : float
        Equivalente onafhankelijke mechanismelengte [m]
    list_dsn : list of UittredepuntElement
        Lijst met elementen met minimaal de attributen:
        - ``M_value`` (float): positie langs M-as (wordt gebruikt voor sorteren
          en voor afbakenen van de lokale lengte).
        - ``pof`` (float): lokale probability of failure (faalkans) op het
        punt.
        - ``a`` (float): karakteristieke lengte-/vormparameter voor
        `bepaal_N_vak`.
    M_van : float
        Ondergrens van het M-bereik voor de eerste halve-afstand (alleen van
        toepassing voor de berekening van `L_van` bij de eerste index).
    M_tot : float
        Bovengrens van het M-bereik voor de laatste halve-afstand (alleen van
        toepassing voor de berekening van `L_tot` bij de laatste index).

    Returns
    -------
    float
        De som van `pof * N_vak` over de uittredepunten.
    """
    list_dsn.sort(key=attrgetter("M_value"))
    pofs: list[float] = []
    for i in range(len(list_dsn)):
        if i == 0:
            L_van: float = M_van
        else:
            L_van: float = (cast(float, list_dsn[i-1].M_value)
                            + (cast(float, list_dsn[i].M_value)
                               - cast(float, list_dsn[i-1].M_value)) / 2)
        if i == len(list_dsn)-1:
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

    sum_pof = corrected_sum(pofs)
    if pofs != []:
        max_pof = max(pofs)
    else:
        max_pof = 0.0

    return sum_pof, max_pof
