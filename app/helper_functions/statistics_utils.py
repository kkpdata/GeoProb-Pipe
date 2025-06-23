from scipy.stats import norm


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