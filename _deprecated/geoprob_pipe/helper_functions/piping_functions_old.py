"""This module contains multiple functions as defined in :cite:t:`sh_piping_2021`"""

import math

# ###########################################################################################################
# General functions
# ###########################################################################################################


# noinspection PyPep8Naming
def calc_Dcover(
    bodemhoogte: float, zandhoogte: float
) -> float:  # Functie voor berekening deklaagdikte
    r"""

    Berekening deklaagdikte, de minimale dikte van de deklaag is 0.1 m omdat negatieve deklaagdiktes niet mogelijk zijn.

    Returns:
        float: deklaagdikte in m
    """
    return max(bodemhoogte - zandhoogte, 0.1)


# noinspection PyPep8Naming
def calc_h_exit(n_a: float, n_b: float):
    r"""Berekening van het niveau van het uittredepunt op basis van polderpeil of maaiveldniveau.
    Functie geeft de maximale waarde van n_a en n_b terug.

    Args:
        n_a (float): niveau 1(polderpeil) in m+NAP
        n_b (float): niveau 2 (maaiveldniveau) in m+NAP

    Returns:
        float: niveau bij het uittredepunt in m+NAP
    """
    return max(n_a, n_b)


# noinspection PyPep8Naming
def calc_dH_red(h: float, h_exit: float, rc: float, Dcover: float) -> float:
    r"""Berekening van het gereduceerde verval over een waterkering

    Args:
        h (float): buitenwaterstand in m+NAP
        h_exit (float): niveau bij het uittredepunt in m+NAP
        rc (float): reductiefactor van het verval evenredig met de dikte van de deklaag [-]
        Dcover (float): deklaagdikte in m

    Returns:
        float: gereduceerd verval in m
    """
    return h - h_exit - rc * Dcover


# ###########################################################################################################
# Functions for uplift and heave
# ###########################################################################################################


# Berekening grenspotentiaal
def calc_d_pot_c_u(d_cover: float, gamma_sat_cover: float, gamma_w: float) -> float:
    r"""Berekening grenspotentiaal ten opzichte van maaiveldniveau.

    Args:
        d_cover (float): deklaagdikte in meters
        gamma_sat_cover (float): verzadigd volumegewicht van de deklaag in kN/m³
        gamma_w (float): volumegewicht van water in kN/m³

    Returns:
        float: grenspotentiaal in meters ten opzichte van maaiveldniveau
    """
    return d_cover * (gamma_sat_cover - gamma_w) / gamma_w


# noinspection PyPep8Naming
# Berekening Z-functie opbarsten
def calc_Z_u(d_pot_c_u: float, pot_exit: float, h_exit: float, mu: float) -> float:
    """ Grenstoestandfunctie voor opbarsten (uplift).

    :param d_pot_c_u: Grenspotentiaal in meters ten opzichte van maaiveldniveau.
    :param pot_exit: Stijghoogte ter plaatse van uittredepunt in m+NAP.
    :param h_exit: Niveau bij het uittredepunt in m+NAP.
    :param mu: Modelfactor voor uplift.
    :return: Z waarde van de grenstoestandfunctie voor opbarsten
    """

    return mu * d_pot_c_u - (pot_exit - h_exit)


# Berekening veiligheidsfactor opbarsten op basis van stijghoogte
# noinspection PyPep8Naming
def calc_F_u(d_pot_c_u: float, pot_exit: float, h_exit: float) -> float:
    r"""Berekening van de veiligheidsfactor voor opbarsten op basis van effectieve spanningen

    Args:
        d_pot_c_u (float): grenspotentiaal in meters ten opzichte van maaiveldniveau
        pot_exit (float): stijghoogte ter plaatse van uittredepunt in m+NAP
        h_exit (float): niveau bij het uittredepunt in m+NAP

    Returns:
        float: veiligheidsfactor voor opbarsten op basis stijghoogte
    """
    if pot_exit <= h_exit:
        Fu = 8.00
    else:
        Fu = d_pot_c_u / (pot_exit - h_exit)
    return Fu


# Berekening veiligheidsfactor opbarsten op basis van spanningen
# noinspection PyPep8Naming
def calc_F_u_macro(
    d_cover: float,
    gamma_sat_cover: float,
    gamma_w: float,
    pot_exit: float,
    h_exit: float,
) -> float:
    r"""Berekening van de veiligheidsfactor voor opbarsten op basis van spanningen ter plaatse van scheidingsvlak
    tussen deklaag en zandlaag. Deze methode wordt toegepast bij macrostabiliteit.

    Args:
        d_cover (float): deklaagdikte in meters
        gamma_sat_cover (float): verzadigd volumegewicht van de deklaag in kN/m³
        gamma_w (float): volumegewicht van water in kN/m³
        pot_exit (float): stijghoogte ter plaatse van uittredepunt in m+NAP
        h_exit (float): niveau bij het uittredepunt in m+NAP

    Returns:
        float: veiligheidsfactor voor opbarsten op basis van spanningen
    """
    if pot_exit <= h_exit:
        Fu = 8.00
    else:
        # opwaartse waterdruk in WVP
        sigma_w = (pot_exit - (h_exit - d_cover)) * gamma_w
        # neerwaartse druk grond
        sigma_g = d_cover * gamma_sat_cover
        # Fu_macro is verhouding neerwaarts / opwaarts
        Fu = sigma_g / sigma_w
    return Fu


def calc_i_optredend(
    pot_exit: float, h_exit: float, d_cover: float
) -> float:  # Berekening optreden heave gradient
    r"""Berekening van de optredende heave gradient. De heave gradient is het stijghoogteverschil over de deklaag
    gedeeld door de deklaagdikte.

    Args:
        pot_exit (float): stijghoogte in het watervoerende zandpakket ter plaatse van uittredepunt in m+NAP
        h_exit (float): niveau bij het uittredepunt in m+NAP
        d_cover (float): deklaagdikte in m

    Returns:
        float: heave gradient in [-]
    """
    return (pot_exit - h_exit) / d_cover


# noinspection PyPep8Naming
def calc_Z_h(
    i_c_h: float, i_optredend: float, mh: float
) -> float:  # Berekening Z-functie heave
    r"""Berekening van de grenstoestandfunctie voor heave

    Args:
        i_c_h (float): kritische heave gradient in [-]
        i_optredend (float): optredende heave gradient in [-]
        mh:

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return (mh * i_c_h) - i_optredend


# noinspection PyPep8Naming
def calc_F_h(
    i_c_h: float, i_optredend: float
) -> float:  # Berekening veiligheidsfactor heave
    r"""

    Berekening van de veiligheidsfactor F_h voor heave. Als de optredende heave gradient negatief is, wordt de
    veiligheidsfactor op 5.00 gezet.

    Args:
        i_c_h (float): kritische heave gradient in [-]
        i_optredend (float): optredende heave gradient in [-]

    Returns:
        float: veiligheidsfactor voor heave
    """
    if i_optredend <= 0:
        F_h = 8.00
    else:
        F_h = i_c_h / i_optredend
    return F_h


# ###########################################################################################################
# functions piping
# ###########################################################################################################


# noinspection PyPep8Naming
# functions from PipingCalculationUtilities
def calc_dH_sellmeijer_inc_calc_settings(
    d70: float,
    k_z: float,
    D: float,
    L: float,
    gamma_w: float,
    visc: float,
    theta: float,
    coefficient_white: float,
    d70_ref: float,
    gamma_p: float,
) -> float:  # Functie voor berekening kritiek verval Sellmeijer
    r"""Berekening kritiek verval methode Sellmeijer inclusief berekeningsinstellingen

    Args:
        d70 (float): 70% percentiel van de korrelgrootteverdeling in meters
        k_z (float): doorlatendheid zandlaag in m/d
        D (float): dikte van de zandlaag in meters
        L (float): kwelweglengte in meters
        gamma_w (float): volumegewicht van water in kN/m³
        visc (float): kinematische viscositeit in m²/s
        theta (float): rolweerstandshoek in graden (37.0)
        coefficient_white (float): coefficiënt van White (0.25)
        d70_ref (float): gemiddelde d70 in kleine schaalproeven (2.08E-4 m)
        gamma_p (float): (schijnbaar) volumegewicht van de zandkorrels onder water in kN/m³ (26.0)

    Returns:
        float: kritiek verval in m
    """
    # Omrekenen doorlatendheid van m/d naar m/s
    k = k_z / (24 * 3600)
    # Intrinsieke doorlatendheid
    k_intr = (visc / 9.81) * k
    # Berekening Fres
    Fres = (
        coefficient_white
        * ((gamma_p - gamma_w) / gamma_w)
        * math.tan(theta * math.pi / 180.00)
    )
    # Fres = 0.25 * ((26.0 - gamma_w) / gamma_w) * math.tan(37.0 * math.pi / 180.00)
    # Berekening Fscale
    Fscale = pow(d70 / d70_ref, 0.4) * d70_ref / pow(k_intr * L, (1.0 / 3.0))
    # Berekening Fgeometry
    if D == L:
        D = D - 0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D / L, 2.8) - 1.0))
    Fgeom = 0.91 * pow(D / L, totdemacht)
    return Fres * Fscale * Fgeom * L


# noinspection PyPep8Naming
# Deze functie is gevalideerd aan de resultaten in Riskeer. Dit is de functie van de LBO1 piping berekening.
# Het verschil met de andere functie is de dat de rolweerstandshoek en sleepkrachtfactor als input worden gegeven.
def calc_dH_sellmeijer(
    d70: float, k_z: float, D: float, L: float, gamma_w: float
) -> float:  # Functie voor berekening kritiek verval Sellmeijer
    r"""Berekening kritiek verval methode Sellmeijer

    Args:
        d70 (float): 70% percentiel van de korrelgrootteverdeling in meters
        k_z (float): doorlatendheid zandlaag in m/d
        D (float): dikte van de zandlaag in meters
        L (float): kwelweglengte in meters
        gamma_w (float): volumegewicht van water in kN/m³

    Returns:
        float: kritiek verval in m
    """
    # Omrekenen doorlatendheid van m/d naar m/s
    k = k_z / (24 * 3600)
    # Intrinsieke doorlatendheid
    k_intr = (0.00000133 / 9.81) * k
    # Berekening Fres
    Fres = 0.25 * ((26.0 - gamma_w) / gamma_w) * math.tan(37.0 * math.pi / 180.00)
    # Berekening Fscale
    Fscale = pow(d70 / 2.08e-4, 0.4) * 2.08e-4 / pow(k_intr * L, (1.0 / 3.0))
    # Berekening Fgeometry
    if D == L:
        D = D - 0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D / L, 2.8) - 1.0))
    Fgeom = 0.91 * pow(D / L, totdemacht)
    return Fres * Fscale * Fgeom * L


# noinspection PyPep8Naming
def calc_Z_p(dhc: float, dhred: float, mp: float) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Args:
        mp (float): modelfactor voor piping
        dhc (float): kritiek verval in meters
        dhred (float): gereduceerd verval in meters

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return (mp * dhc) - dhred


# noinspection PyPep8Naming
def calc_F_p(dhc: float, dhred: float) -> float:
    r"""Berekening van de veiligheidsfactor F_p voor piping. Als het gereduceerde verval kleiner of gelijk aan 0.01,
    wordt gerekend met een gereduceerd verval van 0.01._

    Args:
        dhc (float): kritiek verval in meters
        dhred (float): gereduceerd verval in meters

    Returns:
        float: veiligheidsfactor voor piping
    """
    return dhc / max(dhred, 0.01)
