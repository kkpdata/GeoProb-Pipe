from scipy.stats import norm
import math
from typing import Optional
from scipy.stats import lognorm, norm


def calc_kar_waarde_lognormal(
        mean: float, percentiel: float, sd: Optional[float] = None, vc: Optional[float] = None, shift: float = 0.0
) -> float:
    r""" Berekening van de percentiel waarde van een lognormale verdeling met standaarddeviatie/variatie coëfficient
    en verschuiving.

    Args:
       mean (float): verwachtingswaarde van de lognormale verdeling
       sd (float): standaarddeviatie van de lognormale verdeling, verplicht indien vc niet gegeven
       vc (float): variatie coëfficient van de lognormale verdeling, verplicht indien sd niet gegeven
       percentiel (float): percentiel waarvoor de waarde van de lognormale verdeling wordt berekend. Waarde tussen 0.0 en 1.0.
       shift (float, optional): verschuiving. Defaults to 0.0.

    Returns:
       float: percentiel waarde van de lognormale verdeling
    """

    # Format input arguments
    if sd is None and vc is None:
        raise ValueError(
            f"Provide either the standard deviation (input argument sd), or the variation coefficient (vc).")
    if sd is None:
        sd = vc * mean

    # Logic
    vc_shift = float(sd / (mean - shift))
    log_sd = math.sqrt(math.log(1.0 + math.pow(vc_shift, 2.0)))
    log_mu = math.log(mean - shift) - 0.5 * math.pow(log_sd, 2.0)
    kar_waarde = float(lognorm.ppf(percentiel, s=log_sd, loc=0.0, scale=math.exp(log_mu))) + shift

    return kar_waarde


def calc_kar_waarde_normal(mean: float, std: float, percentiel: float) -> float:
    """Berekening van de percentiel waarde van een normale verdeling

    Args:
        mean (float): verwachtingswaarde van de normale verdeling
        std (float): standaarddeviatie van de normale verdeling
        percentiel (float): percentiel waarvoor de waarde van de normale verdeling wordt berekend

    Returns:
        float: percentiel waarde van de normale verdeling
    """
    return float(norm.ppf(percentiel, loc= mean, scale=std))


def convert_failure_probability_to_beta(failure_probability: float) -> float:
    """Converts failure probability (Pf) to the reliability index (β).

    The reliability index is the negative inverse of the standard normal
    cumulative distribution function (Φ) applied to the failure probability.

    β = -1 * Φ⁻¹(Pf)

    Args:
        failure_probability (float): failure probability (Pf)

    Returns:
        float: reliability index (β)
    """
    return float(-1 * norm.ppf(failure_probability))
