r"""Module met functies voor het berekenen van fysische componenten van piping en uplift. Dit betreft onder andere de dikte van de deklaag,het niveau bij het uittredepunt en de kwelweglengte.
"""

import math
from geoprob_pipe.calculations.physical_components.model4a import Model4a


def calc_d_deklaag(
        mv_exit: float,
        top_zand: float
) -> float:
    r"""Berekening deklaagdikte ter plaatse van het uittredepunt, de minimale dikte van de deklaag is 0.1 m omdat negatieve deklaagdiktes niet mogelijk zijn. Dit uitgangspunt is gekozen omdat ook bij een zeer dunne deklaag nog enige reductie van het verval verwacht mag worden. 

    Args:
        mv_exit (float): Bodemhoogte ter plaatse van Uittredepunten [m+NAP]
        top_zand (float): Geschematiseerde top van het vak [m+NAP]

    Returns:
        float: deklaagdikte [m]
    """
    return max(mv_exit - top_zand, 0.1)


def calc_h_exit(
        polderpeil: float,
        mv_exit: float
) -> float:
    r"""Berekening van het niveau van het uittredepunt op basis van polderpeil of maaiveldniveau.
    Functie geeft de maximale waarde van polderpeil en mv_exit terug. Dit is de benedenstroomse randvoorwaarde voor het verval in pipingberekeningen.

    Args:
        polderpeil (float): polderpeil [m+NAP]
        mv_exit (float): maaiveldniveau van uittredepunt [m+NAP]

    Returns:
        float: niveau bij het uittredepunt in m+NAP
    """
    return max(polderpeil, mv_exit)


# noinspection PyPep8Naming
def calc_lengte_voorland(
        L_intrede: float,
        L_but: float
) -> float:
    r"""Berekent de geometrische voorlandlengte in [m] op basis van afstanden ten opzichte van een uittredepunt. In de pre-processing tool worden :math:`L_{intrede}` en :math:`L_{but}` als geografische lijnobjecten gedefinieerd. De kortste afstand tussen deze objecten is invoer voor deze functie.

    Args:
        L_intrede (float): afstand van uittredepunten tot een (denkbeeldige) intredelijn [m]
        L_but (float): afstand van uittredepunten tot buitenteenlijn [m]

    Returns:
        float: geometrische voorlandlengte [m]
    """
    return abs(L_intrede - L_but)


# noinspection PyPep8Naming
def calc_lambda_achterland(
        kD_wvp: float,
        c_achterland: float
) -> float:
    r"""Berekent de spreidingslengte van het achterland in [m].

    .. math::

        \lambda = \sqrt{kDc}

    Args:
        kD_wvp (float): Transmissiviteit van het watervoerende pakket [m²/dag]
        c_achterland (float): Weerstand van de deklaag in het achterland [dag]

    Returns:
        float: spreidingslengte van het achterland [m]
    """
    return (kD_wvp * c_achterland) ** (1 / 2)


# noinspection PyPep8Naming
#TODO: functie samenvoegen met calc_lambda_achterland?
def calc_lambda_voorland(
        kD_wvp: float,
        c_voorland: float
) -> float:
    r"""Berekent de spreidingslengte van het achterland in [m].

    .. math::

        \lambda = \sqrt{kDc}

    Args:
        kD_wvp (float): Transmissiviteit van het watervoerende pakket [m²/dag]
        c_voorland (float): Weerstand van de deklaag in het voorland [dag]

    Returns:
        float: spreidingslengte van het voorland [m]
    """
    return (kD_wvp * c_voorland) ** (1 / 2)


def calc_dh_red(
        buitenwaterstand: float,
        h_exit: float,
        r_c_deklaag: float,
        d_deklaag: float
) -> float:
    r"""Berekening van het gereduceerde verval over de waterkering.

    .. math::
        
        \Delta h_{red} = h_{buitenwaterstand} - h_{exit} - r_{c,deklaag} \cdot d_{deklaag}

    Args:
        buitenwaterstand (float): buitenwaterstand [m+NAP]
        h_exit (float): Benedenstroomse randvoorwaarde verval [m+NAP]
        r_c_deklaag (float): Reductie constante van het verval over de deklaag [-]
        d_deklaag (float): deklaagdikte in m

    Returns:
        float: gereduceerd verval [m]
    """
    return buitenwaterstand - h_exit - r_c_deklaag * d_deklaag


# noinspection PyPep8Naming
def calc_W_achterland(
        lambda_achterland: float,
        L_achterland: float
) -> float:
    r"""Berekent de geohydrologische weerstand van het achterland in [m].

    .. math::

        W = \lambda tanh(\frac{L}{\lambda})

    Args:
        lambda_achterland (float): de spreidingslengte van het achterland [m]
        L_achterland (float): afstand van uittredepunten tot achterlandlengte [m]

    Returns:
        float: geohydrologische weerstand van het achterland [m]
    """
    return lambda_achterland * math.tanh(L_achterland / lambda_achterland)


# noinspection PyPep8Naming
#TODO: functie samenvoegen met calc_W_achterland?
def calc_W_voorland(
        lambda_voorland: float,
        L_voorland: float
) -> float:
    r"""Berekent de geohydrologische weerstand van het voorland in [m]. Dit wordt ook wel de effectieve voorlandlengte genoemd.

    .. math::

        W = \lambda tanh(\frac{L}{\lambda})

    Args:
        lambda_voorland (float): de spreidingslengte van het voorland [m]
        L_voorland (float): Geometrische voorlandlengte [m]

    Returns:
        float: geohydrologische weerstand van het voorland [m]
    """
    return lambda_voorland * math.tanh(L_voorland / lambda_voorland)


# noinspection PyPep8Naming
def calc_L_kwelweg(
        L_but: float,
        W_voorland: float
) -> float:
    r"""Berekent de kwelweglengte in [m].
    De kwelweglengte is de som van de afstand van het uittredepunt tot de buitenteenlijn en de effectieve voorlandlengte van het voorland. De onzekerheid in de kwelweglengte zit in de effectieve voorlandlengte.

    Args:
        L_but (float): afstand van uittredepunten tot buitenteenlijn [m]
        W_voorland (float): geohydrologische weerstand van het voorland [m]

    Returns:
        float: kwelweglengte [m]
    """

    return W_voorland + L_but


def calc_dphi_c_u(
        d_deklaag: float,
        gamma_sat_deklaag: float,
        gamma_water: float
) -> float:
    r"""Berekening grenspotentiaal ten opzichte van maaiveldniveau in [m].

    .. math::

        \Delta \phi_{c,u} = \frac{d_{deklaag} \cdot (\gamma_{sat,deklaag} - \gamma_{w})}{\gamma_{w}}
    
    Args:
        d_deklaag (float): Dikte van de cohesieve deklaag [m]
        gamma_sat_deklaag (float): verzadigd volumegewicht van de deklaag [kN/m³]
        gamma_water (float): volumegewicht van water [kN/m³]

    Returns:
        float: grenspotentiaal ten opzichte van maaiveldniveau [m]
    """
    return d_deklaag * (gamma_sat_deklaag - gamma_water) / gamma_water


def calc_i_exit(
        phi_exit: float,
        h_exit: float,
        d_deklaag: float
) -> float:
    r"""Berekening van de optredende heave gradient. De heave gradient is het stijghoogteverschil over de deklaag gedeeld door de deklaagdikte.

    .. math::

        i_{exit} = \frac{(\phi_{exit} - h_{exit})}{d_{deklaag}}

    Args:
        phi_exit (float): stijghoogte in het watervoerende zandpakket ter plaatse van uittredepunt in m+NAP
        h_exit (float): niveau bij het uittredepunt [m+NAP]
        d_deklaag (float): deklaagdikte [m]

    Returns:
        float: heave gradient in [-]
    """
    return (phi_exit - h_exit) / d_deklaag


# noinspection PyPep8Naming
#TODO: deze wrapper functie wordt gebruikt in heave_icw_model4a.py en uplift_icw_model4a.py 
# check of deze limit_state functies ook daadwerkelijk gebruikt worden in de berekeningen.
# zo niet, verwijder deze functies of roep de model4a klasse direct aan in de limit_state functies.
def calc_r_exit_model4a(
        kD_wvp: float,
        D_wvp: float,
        c_voorland: float,
        c_achterland: float,
        L_but: float,
        L_bit: float,
        L_achterland: float,
        L_voorland: float
) -> float:
    r"""Wrapper functie voor het berekenen van de dempingsfactor bij uittredepunten met behulp van Model4a. De functie gaat uit dat x = 0.0 bij de binnenteen ligt.  Dit betekent dat x_bit = 0.0 en x_but negatief is.
    Uittredepunten moeten altijd binnendijks van de binnenteenlijn liggen.

    """
    model4a = Model4a(
        kD=kD_wvp,
        D=D_wvp,
        c1=c_voorland,
        c3=c_achterland,
        L1=L_voorland,
        L3=L_achterland,
        x_but=-1.0 * abs(L_but - L_bit),  # x_but moet negatief zijn, x_bit is 0.0
        x_bit=0.0, )  # x_bit is 0.0
    # Bereken de respons bij het uittredepunt
    r_exit, _, _ = model4a.respons(L_bit)
    return r_exit


def calc_phi_exit(
        polderpeil: float,
        r_exit: float,
        buitenwaterstand: float
) -> float:  # Van respons naar potentiaal
    r"""Berekent de theoretische stijghoogte bij uittredepunten in [m+NAP].

    .. math::

        \phi_exit(x) = polderpeil + r(x) (buitenwaterstand - polderpeil)

    Args:
        polderpeil (float): Benedenstroomse randvoorwaarde verval [m+NAP]
        r_exit (float): Dempingsfactor bij uittredepunten [-]
        buitenwaterstand (float): buitenwaterstand [m+NAP]

    Returns:
        float: Theoretische stijghoogte bij uittredepunten [m+NAP]
    """
    return polderpeil + r_exit * (buitenwaterstand - polderpeil)


# noinspection PyPep8Naming
# TODO: functies toevoegen in docstring
def calc_dh_c(
        d70: float,
        D_wvp: float,
        kD_wvp: float,
        L_kwelweg: float,
        gamma_water: float,
        g: float,
        v: float,
        theta: float,
        eta: float,
        d70_m: float,
        gamma_korrel: float,
) -> float:
    r"""Berekening kritiek verval methode Sellmeijer inclusief berekeningsinstellingen

    .. math::

    \Delta H_{c} = F_{resistance} \cdot F_{scale} \cdot F_{geometry} \cdot L_{kwelweg}


    Args:
        d70 (float): 70% percentiel van de korrelgrootteverdeling [m]
        D_wvp (float): dikte van het watervoerende pakket [m]
        kD_wvp (float): transmissiviteit van het watervoerende pakket [m²/dag]
        L_kwelweg (float): kwelweglengte in meters
        gamma_water (float): volumegewicht van water [kN/m³]
        g (float): Zwaartekrachtversnelling [m/s2]
        v (float): kinematische viscositeit [m²/s]
        theta (float): rolweerstandshoek [graden]
        eta (float): coefficiënt van White [-]
        d70_m (float): gemiddelde d70 in kleine schaalproeven [m]
        gamma_korrel (float): (schijnbaar) volumegewicht van de zandkorrels onder water [kN/m³]

    Returns:
        float: kritiek verval [m]
    """
    # Berekenen van de doorlatendheid
    k_wvp_calc = kD_wvp / D_wvp  # Omrekenen transmissiviteit naar doorlatendheid

    # Omrekenen doorlatendheid van m/d naar m/s
    k_wvp_calc_sec = k_wvp_calc / (24 * 3600)
    # Intrinsieke doorlatendheid
    k_intr = (v / g) * k_wvp_calc_sec

    # Berekening Fres
    # noinspection PyPep8Naming
    Fres = (
            eta
            * ((gamma_korrel - gamma_water) / gamma_water)
            * math.tan(theta * math.pi / 180.00)
    )

    # Berekening Fscale
    # noinspection PyPep8Naming
    Fscale = pow(d70 / d70_m, 0.4) * d70_m / pow(k_intr * L_kwelweg, (1.0 / 3.0))

    # Berekening F_geometry
    if D_wvp == L_kwelweg:
        # noinspection PyPep8Naming
        D_wvp = D_wvp - 0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D_wvp / L_kwelweg, 2.8) - 1.0))
    # noinspection PyPep8Naming
    Fgeom = 0.91 * pow(D_wvp / L_kwelweg, totdemacht)

    return Fres * Fscale * Fgeom * L_kwelweg

