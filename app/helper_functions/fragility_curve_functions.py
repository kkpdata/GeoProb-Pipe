"""
References:
https://github.com/Deltares/GEOLib/blob/d07e708d38b01d3d2e134de6310c16c8c781f3be/docs/community/tutorial_dstability_fragility_curve.rst
https://deltares.github.io/GEOLib-Plus/latest/community/probabilistic_macrostability/Tutorial_3_Fragility_Curve_Integration.html
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import gumbel_r, norm

from app.classes.waterlevel_statistics import WaterlevelStatistics
from app.helper_functions.plotting_functions import plot_waterlevel_statistics


def densify_extrapolate(
    waterlevels: pd.Series,
    betas: pd.Series,
    waterlevel_range_start: float,
    waterlevel_range_end: float,
    waterlevel_delta: float,
) -> pd.DataFrame:
    """Generates a denser set of waterlevels within a specified range, applies linear interpolation
    (and extrapolation if needed) to estimate corresponding beta-values, and returns the resulting
    waterlevel-beta pairs.

    Args:
        waterlevels (pd.Series): waterlevels for which probabilistic calculations were carried out
        betas (pd.Series): beta values corresponding to the abovementioned waterlevels
        waterlevel_range_start (float): start of waterlevel range for which new values are found using extrapolation
        waterlevel_range_end (float): end of waterlevel range for which new values are found using extrapolation
        waterlevel_delta (float): step size to use between waterlevel_range_start and waterlevel_range_end

    Returns:
        pd.DataFrame: overview of new (additional) waterlevels and corresponding beta values found using extrapolation
    """

    array_new_waterlevels = np.arange(waterlevel_range_start, waterlevel_range_end + waterlevel_delta, waterlevel_delta)
    f = interp1d(waterlevels, betas, kind="linear", bounds_error=False, fill_value="extrapolate")  # type: ignore
    array_new_betas = f(array_new_waterlevels)

    return pd.DataFrame({"new_waterlevel": array_new_waterlevels, "new_beta": array_new_betas})


# TODO alpha bepalen voor de waterstand na integratie(zie Deltares script, moet extra code toegevoegd worden)
def integrating_FC_with_water_levels(
    waterlevels: pd.Series,
    betas: pd.Series,
    waterlevel_statistics: WaterlevelStatistics,
    waterlevel_range: list[float],
    waterlevel_delta: float = 0.1,
) -> tuple[float, float]:
    """Calculates the total failure probability (Pf) by integrating the conditional failure probability
    (fragility curve) over the entire range of possible water levels, weighted by the probability
    density function (PDF) of the water levels.

    The total failure probability is computed as:

    Pf = ∫ FR(h) * fh(h) dh

    Where:
        - FR(h) = P(F|h): The fragility curve, representing the failure probability as a function
          of the water level (h).
        - fh(h): The probability density function of the water level, assumed to follow a Gumbel
          distribution in this context.

    The function performs the following steps:
        1. Interpolates and extrapolates between the provided fragility curve points to create a denser
        set of data points.
        2. Calculates the PDF of the water level using the Gumbel distribution.
        3. Integrates the product of the fragility curve and the PDF over the range of water levels to
        compute the total failure probability (Pf).
        4. Evaluates the reliability index (Beta) based on the calculated Pf.

    Args:
        waterlevels (pd.Series): waterlevels for which probabilistic calculations were carried out
        betas (pd.Series): beta values corresponding to the abovementioned waterlevels
        waterlevel_statistics (WaterlevelStatistics): waterlevel statistics mu (mode) and sigma (standard deviation) (Gumbel fit)
        waterlevel_range (list[float]): range of waterlevels for which we want a integrated fragility curve
        waterlevel_delta (float): step size to use between waterlevel_range_start and waterlevel_range_end. Defaults to 0.1

    Returns:
        tuple[float, float]: (reliability index after integration, total failure probability after integration)
    """

    # Interpolate and extrapolate between fragility curve points, create more points
    df_inter_extrapolated = densify_extrapolate(
        waterlevels,
        betas,
        waterlevel_range[0],
        waterlevel_range[-1],
        waterlevel_delta,
    )

    # Calculating the pdf of the water level 𝑓ℎ(ℎ)
    # Note that a Gumbel distribution is assumed
    df_inter_extrapolated["fh_pdf_waterlevel"] = df_inter_extrapolated["new_waterlevel"].apply(
        lambda h: gumbel_r.pdf(h, loc=waterlevel_statistics.mu, scale=waterlevel_statistics.sigma)  # type: ignore
    )  # type: ignore

    # Integrate f(h) with stepsize of delta_h -> 1
    sumFh = sum(df_inter_extrapolated["fh_pdf_waterlevel"]) * waterlevel_delta

    # TODO check Appendix A Handreiking Faalkansanalyse Macro voor uitleg uitintegreren. Verwerk info hieruit in de documentatie van dit script

    # calculating total failure probability Φ[−𝛽(ℎ)]
    P_fh = norm.cdf(-1 * df_inter_extrapolated["new_beta"])  # P(f|h)
    Pf = P_fh * df_inter_extrapolated["fh_pdf_waterlevel"] * waterlevel_delta  # P(f/h)*f(h)*delta
    sumPf = sum(Pf) / sumFh

    # evaluating the relevant reliability index for the obtained failure probability
    beta = -1 * norm.ppf(sumPf)

    print("Sum of $f_h$ = ", sumFh)
    print("Total failure probability after integration = %0.2e" % (sumPf))
    print("Reliability index after integration = ", beta)

    # Plot waterlevel statistics including fragility curve
    plot_waterlevel_statistics(
        waterlevels,
        betas,
        df_inter_extrapolated,
        waterlevel_statistics,
    )

    return float(beta), float(sumPf)
