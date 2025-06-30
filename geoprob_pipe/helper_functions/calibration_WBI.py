"""This module contains calibration functions derived from the WBI2017 project
"""

import math
from dataclasses import dataclass 
from scipy.stats import norm

# noinspection PyPep8Naming
def calc_Beta_u(
    F_u: float, Bnorm: float
) -> float:  # Berekening van veiligheidsfactor naar benaderde beta voor opbarsten
    r"""Calculation of the estimated reliability index of uplift based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::
        \beta_u = \frac{ln(F_{u}/0.48) + 0.27 \cdot \beta_{norm}}{0.46}


    Args:
        F_u (float): safety factor for uplift
        Bnorm (float): required reliability index of the dike trajectory

    Returns:
        float: estimated reliability index for uplift failure mechanism
    """
    return (
        math.log(F_u / 0.48) + (-0.27 * Bnorm)
    ) / 0.46  #'Bnorm' is in python a negative value therefore -1*Bnorm


# noinspection PyPep8Naming
def calc_Beta_h(
    F_h: float, Bnorm: float
) -> float:  # Berekening van veiligheidsfactor naar benaderde beta voor heave
    r"""Calculation of the estimated reliability index of heave based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::

        \beta_h = \frac{ln(F_{h}/0.37) + 0.30 \cdot \beta_{norm}}{0.48}

    Args:
        F_h (float): safety factor for heave
        Bnorm (float): required reliability index for the dike trajectory

    Returns:
        float: estimated reliability index for heave failure mechanism
    """
    return (
        math.log(F_h / 0.37) + (-0.30 * Bnorm)
    ) / 0.48  # 'Bnorm' is in python a negative value therefore -1*Bnorm


# noinspection PyPep8Naming
def calc_Beta_p(
    F_p: float, Bnorm: float
) -> float:  # Berekening van veiligheidsfactor naar benaderde beta voor piping
    r"""Calculation of the estimated reliability index of piping based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::

        \beta_p = \frac{ln(F_{p}/1.04) + 0.43 \cdot \beta_{norm}}{0.37}


    Args:
        F_p (float): safety factor for piping
        Bnorm (float): required reliability index of the dike trajectory

    Returns:
        float: estimated reliability index for piping failure mechanism
    """
    return (
        math.log(F_p / 1.04) + (-0.43 * Bnorm)
    ) / 0.37  ##'Bnorm' is in python a negative value therefore -1*Bnorm


# noinspection PyPep8Naming
def calc_SF_u(B_cross: float, Bnorm: float) -> float:
    r"""Calculation of the required safety factor for uplift based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::

        \gamma_u = 0.48 \cdot e^{0.46 \cdot - \beta_{cross} - 0.27 \cdot - \beta_{norm}}


    Args:
        B_cross (float): required reliability index for uplift in cross-section (negative value)
        Bnorm (float): required reliability index of the dike trajectory (negative value)

    Returns:
        float: safety factor for uplift failure mechanism
    """
    return 0.48 * math.exp(0.46 * -1.0 * B_cross - 0.27 * -1.0 * Bnorm)


# noinspection PyPep8Naming
def calc_SF_h(B_cross: float, Bnorm: float) -> float:
    r"""Calculation of the required safety factor for heave based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::

        \gamma_h = 0.37 \cdot e^{0.48 \cdot - \beta_{cross} - 0.30 \cdot - \beta_{norm}}


    Args:
        B_cross (float): required reliability index for heave in cross-section (negative value)
        Bnorm (float): required reliability index of the dike trajectory (negative value)

    Returns:
        float: safety factor for heave failure mechanism
    """
    return 0.37 * math.exp(0.48 * -1.0 * B_cross - 0.30 * -1.0 * Bnorm)


# noinspection PyPep8Naming
def calc_SF_p(B_cross: float, Bnorm: float) -> float:
    r"""Calculation of the required safety factor for piping based on the WBI2017 calibration

    see :cite:t:`calibration_piping_2016`

    math::

        \gamma_p = 1.04 \cdot e^{0.37 \cdot - \beta_{cross} - 0.43 \cdot - \beta_{norm}}


    Args:
        B_cross (float): required reliability index for piping in cross-section (negative value)
        Bnorm (float): required reliability index of the dike trajectory (negative value)

    Returns:
        float: safety factor for piping failure mechanism
    """
    return 1.04 * math.exp(0.37 * -1.0 * B_cross - 0.43 * -1.0 * Bnorm)

@dataclass
class ReliabilityDikeTrajectory:
    """ Class to store the reliability of a dike trajectory and calculate the required cross-section reliability
    indices and safety factors"""

    T: float
    w: float
    L: float
    a: float
    b: float

    # noinspection PyPep8Naming
    @property
    def Pnorm(self) -> float:
        return 1.0 / self.T

    # noinspection PyPep8Naming
    @property
    def P_failure_mechanism(self) -> float:
        return self.w / self.T

    # noinspection PyPep8Naming
    @property
    def Bnorm(self) -> float:
        return float(norm.ppf(self.Pnorm))

    # noinspection PyPep8Naming
    @property
    def B_failure_mechanism(self) -> float:
        return float(norm.ppf(self.P_failure_mechanism))

    # noinspection PyPep8Naming
    @property
    def N_dsn(self) -> float:
        return 1.0 + (self.a * self.L) / self.b

    # noinspection PyPep8Naming
    @property
    def P_cross(self) -> float:
        return self.P_failure_mechanism / self.N_dsn

    # noinspection PyPep8Naming
    @property
    def B_cross(self) -> float:
        return float(norm.ppf(self.P_cross))

    # noinspection PyPep8Naming
    @property
    def SF_u(self) -> float:
        return calc_SF_u(self.B_cross, self.Bnorm)

    # noinspection PyPep8Naming
    @property
    def SF_h(self) -> float:
        return calc_SF_h(self.B_cross, self.Bnorm)

    # noinspection PyPep8Naming
    @property
    def SF_p(self) -> float:
        return calc_SF_p(self.B_cross, self.Bnorm)
