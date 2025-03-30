"""This module consists of different geohydrological methods used in the safety assesment of levees.

There are different functions and classes defined. Background information can be found in
:cite:t:`trw_2004`.
"""

import math


# Functions
def calc_lambda(kd: float, c: float) -> float:
    r"""Calculates leakage length

    .. math::

        \lambda = \sqrt{kDc}

    Args:
        kd (float): transmissivity [m2/day]
        c (float): resistance of the top soil [day]

    Returns:
        float: returns leakage length lambda [m]
    """
    return math.sqrt(kd * c)


# W staat voor de effectieve voorlandlengteformule, lam = lambda
def calc_W(lam: float, L: float) -> float:
    r"""Calculates effective leakage length by:

    .. math::

        W = \lambda tanh(\frac{L}{\lambda})

    Args:
        lam (float): leakage lengte [m]
        L (float): physical length [m]

    Returns:
        float: effective leakage length [m]
    """
    return lam * math.tanh(L / lam)


def calc_r_BIT(w1: float, l2: float, w3: float) -> float:
    r"""Calculates response in stationary models at innertoe based on given weights.

    .. math::

        r_{BIT} = \frac{W_{3}}{W_{1} + L_{2} + W_{3}}

    Args:
        w1 (float): weight of foreland [m]
        l2 (float): length of dike base [m]
        w3 (float): weight of hinterland [m]

    Returns:
        float: response at inner toe [0.0-1.0]
    """
    return (w3) / (w1 + l2 + w3)


def calc_r_BUT(w1: float, l2: float, w3: float) -> float:
    r"""Calculates response in stationary models at outer toe based on given weights.

    .. math::

        r_{BUT} = \frac{L_{2} + W_{3}}{W_{1} + L_{2} + W_{3}}

    Args:
        w1 (float): weight of foreland [m]
        l2 (float): length of dike base [m]
        w3 (float): weight of hinterland [m]

    Returns:
        float: response at outer toe [0.0-1.0]
    """
    return (l2 + w3) / (w1 + l2 + w3)


def calc_respons2pot(
    h_ref: float, r_exit: float, h_riv: float
) -> float:  # Van respons naar potentiaal
    r"""Calculates potential from given response.

    .. math::

        \phi(x) = h_{ref} + r(x) (h_{river} - h_{ref})

    Args:
        h_ref (float): potential in hinterland (polder)
        r_exit (float): response at given location [m]
        h_riv (float): water level at river

    Returns:
        float: potential at given location
    """
    return h_ref + r_exit * (h_riv - h_ref)


def calc_pot2repons(
    phi: float, h_ref: float, h_riv: float
) -> float:  # Van potentiaal naar respons.
    r"""Calculates response from given potential

    .. math::

        r(x) = \frac{\phi(x)-h_{ref}}{h_{river} -h_{ref}}

    Args:
        phi (float): given potential [m+ref]
        h_ref (float): reference leve, eg. potential in polder [m+ref]
        h_riv (float): water level at river, given potential [m+ref]

    Returns:
        float: response given reference level
    """
    return (phi - h_ref) / (h_riv - h_ref)


def calc_ang_frequency(T: float) -> float:
    r"""Calculates Angular frequency from period of a sinus wave.

    .. math::

        \omega = \frac{2 \pi}{T}

    Args:
        T (float): period [s]

    Returns:
        float: angular frequency [rad/s]
    """
    T_float = float(T)
    w = 2.0 * math.pi / T_float
    return w


def calc_P_from_T(T: float) -> float:
    r"""Calculates duration P from period T

    .. math::

        P = \frac{T}{2}

    This is a helper function. Often a period T needs to be
    from a known storm surge P

    Args:
        T (float): Storm period T [s]

    Returns:
        float: Storm duration P [s]
    """
    return T / 2.0


def calc_T_from_P(P: float) -> float:
    r"""Calculates storm period from storm duration P

    .. math::

        T = P * 2.0

    Args:
        P (float): Storm duration P [s]

    Returns:
        float: Storm period T [s]
    """
    return P * 2.0


# functies voor berekening cyclische spreidingslengte op basis van de stationaire spreidingslengte
def calc_lambda_cycl_from_stationnary(
    LambdaStat: float, d: float, c_v: float, w: float
) -> float:
    r"""Calculates cyclic lambda from stationary leakage length

    see :cite:t:`bauduin_barends_1988`

    .. math::

        t_{h} = \frac{d^{2}}{c_{v}^{'}}

        \lambda_{\omega} = \frac{1.082 * \lambda_{s}}{\sqrt[4]{t_{h}^{'}\omega}}


    Args:
        LambdaStat (float): stationary leakage length [m]
        d (float): thickness of impermeable cover layer [m]
        c_v (float): one dimensional consolidation coëfficiënt  [m2/s]
        w (float): angular frequency [rad/s]

    Returns:
        float: cyclic lambda [m]
    """
    th = math.pow(d, 2.0) / c_v
    LambdaCycl = (1.082 * LambdaStat) / math.pow(th * w, 0.25)
    return LambdaCycl


def calc_lambda_cycl(LambdaCycl_1: float, T2: float, T1: float) -> float:
    r"""Calculates cyclic lambda from one period to another

    .. math::

        \lambda_{\omega, T_{2}}^{'} = \lambda_{\omega, T_{1}}^{'} \sqrt[4]{\frac{T_{2}}{T_{1}}}

    T1 and T2 are in same dimension (e.g. seconds, hours, days)

    Args:
        LambdaCycl_1 (float): known cyclic lambda at given period T1
        T2 (float): period for which cyclic lambda needs te be calculated
        T1 (float): known period

    Returns:
        float: _description_
    """
    return LambdaCycl_1 * math.pow(T2 / T1, 0.25)


def calc_theta(b: float, lambda_w_vl: float) -> float:
    r"""Calculates theta, see figure b4.13 from 'Technisch Rapport Waterspanningen bij dijken' :cite:t:`trw_2004`.
    Approximation by 5th degree polynomials.

    Args:
        b (float): with of river [m],
        lambda_w_vl (float): cyclic lambda of foreland [m]

    Raises:
        ValueError: Only for positive numbers

    Returns:
        float: theta from b4.13 :cite:t:`trw_2004`
    """
    x = b / lambda_w_vl
    if x < 0.0:
        raise ValueError
    elif x > 2.8:
        return 0.0
    else:
        return (
            0.0078 * math.pow(x, 5.0)
            - 0.082 * math.pow(x, 4.0)
            + 0.3139 * math.pow(x, 3.0)
            - 0.4683 * math.pow(x, 2.0)
            + 0.035 * x
            + 0.392699081698724
        )


def calc_f(b: float, lambda_w_vl: float) -> float:
    (
        r"""Calculates f, see figure b4.13 from 'Technisch Rapport Waterspanningen bij dijken' :cite:t:`trw_2004`. 
    Approximation by exponential function

    Args:
        b (float): with of river [m], 
        lambda_w_vl (float): cyclic lambda of foreland [m]
        
    Raises:
        ValueError: Only for positive numbers

    Returns:
        float: f from b4.13 :cite:t:`trw_2004`
    """
        """
    b           : with of river in m
    lambda_w_vl : cyclic lambda of foreland"""
    )
    x = b / lambda_w_vl
    if x < 0.0:
        raise ValueError
    else:
        return 1.0 + 7.0659 * math.exp(-3.648 * x)


def calc_mean_pot_gradient(
    W1: float, W3: float, x_tp: float, mean_wl: float, phi_onv: float
) -> float:
    r"""Approximation of hydraulic head under daily (mean) conditions.
    Uses method from tipping point :cite:t:`trw_2004`

    .. math::

       \phi(x) = h_{ref} + r(x) (h_{rivier} - h_{ref})

        r(x) = \frac{exp(\frac{- x_{tp}}{W_{3}})}{1+\frac{W_1}{W_3}}

    Args:
        W1 (float): weight of foreland under daily conditions [m]
        W3 (float): weight of hinterland under daily conditions [m]
        x_tp (float): given location from tipping point [m]
        mean_wl (float): daily water level at river
        phi_onv (float): potential in hinterland (polder)

    Returns:
        float: hydraulic head at given distance from tipping point
    """
    # Calculates respons tipping point
    rk = 1 / (1 + (W1 / W3))
    # Calculates response at given distance from tipping point
    r_uit = math.exp(-1 * (x_tp / W3))
    # Calculates hydraulic head at given distance from tipping point
    return phi_onv + (mean_wl - phi_onv) * rk * r_uit
