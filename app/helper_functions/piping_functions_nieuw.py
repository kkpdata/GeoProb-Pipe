import math

from .model4a import Model4a

###################################################################################
# Functies hieronder direct volgend uit variabelen van input.xlsx
###################################################################################

def calc_d_deklaag(
    mv_exit: float, 
    top_zand: float
    ) -> float:  
    r"""

    Berekening deklaagdikte, de minimale dikte van de deklaag is 0.1 m omdat negatieve deklaagdiktes niet mogelijk zijn.

    Args:
        mv_exit (float): Bodemhoogte ter plaatse van Uittredepunten [m+NAP]
        top_zand (float): Geschematiseerde top van het zak in het vak [m+NAP]

    Returns:
        float: deklaagdikte [m]
    """
    return max(mv_exit - top_zand, 0.1)


def calc_h_exit(
    polderpeil: float, 
    mv_exit: float
    ) -> float:
    r"""Berekening van het niveau van het uittredepunt op basis van polderpeil of maaiveldniveau.
    functie geeft de maximale waarde van polderpeil en mv_exit terug.

    Args:
        polderpeil (float): polderpeil [m+NAP]
        mv_exit (float): maaiveldniveau van uittredepunt [m+NAP]

    Returns:
        float: niveau bij het uittredepunt in m+NAP
    """
    return max(polderpeil, mv_exit)


def calc_L_dijk(
    L_bit: float, 
    L_but: float
    ) -> float:
    r"""Berekent de dijkzate in m

    Args:
        L_bit (float): afstand van uittredepunten tot binnenteenlijn [m]
        L_but (float): afstand van uittredepunten tot buitenteenlijn [m]  

    Returns:
        float: dijkzate [m] 
    """
    return abs(L_but - L_bit)


def calc_L_voorland(
    L_intrede: float, 
    L_but:float
    ) -> float:
    r"""Berekent de geometrische voorlandlengte in m

    Args:
        L_intrede (float): afstand van uittredepunten tot binnenteenlijn [m]
        L_but (float): afstand van uittredepunten tot buitenteenlijn [m]

    Returns:
        float: geometrische voorlandlengte [m]
    """
    return abs(L_intrede - L_but)


def calc_lambda_achterland(
    kD_wvp: float, 
    c_achterland: float
    ) -> float:
    r"""Berekent de spreidingslengte van het achterland in m

    .. math::

        \lambda = \sqrt{kDc}

    Args:
        kD (float): Transmissiviteit van het watervoerende pakket [m2/dag]
        c_achterland (float): Weerstand van de deklaag in het achterland [dag]

    Returns:
        float: spreidingslengte van het achterland [m]
    """
    return (kD_wvp * c_achterland)**(1/2)


def calc_lambda_voorland(
    kD_wvp: float, 
    c_voorland: float
    ) -> float:
    r"""Berekent de spreidingslengte van het achterland in m

    .. math::

        \lambda = \sqrt{kDc}

    Args:
        kD (float): Transmissiviteit van het watervoerende pakket [m2/dag]
        c_voorland (float): Weerstand van de deklaag in het voorland [dag]

    Returns:
        float: spreidingslengte van het voorland [m]
    """
    return (kD_wvp * c_voorland)**(1/2)

###################################################################################
# Functies hieronder bevatten uitkomsten uit bovenliggnde functies als input
###################################################################################

def calc_dh_red(
    buitenwaterstand: float, 
    h_exit: float, 
    r_c_deklaag: float, 
    d_deklaag: float
    ) -> float:
    r"""Berekening van het gereduceerde verval over de waterkering

    Args:
        buitenwaterstand (float): buitenwaterstand [m+NAP]
        h_exit (float): Benedestroomse randvoorwaarde verval [m+NAP]
        r_c_deklaag (float): Reductieconstante van het verval over de deklaag [-]
        d_deklaag (float): deklaagdikte in m

    Returns:
        float: gereduceerd verval [m]
    """
    return buitenwaterstand - h_exit - r_c_deklaag * d_deklaag


def calc_W_achterland(
    lambda_achterland: float, 
    L_achterland: float
    ) -> float:
    r"""Berekent de geohydrologische weerstand van het achterland in m

    .. math::

        W = \lambda tanh(\frac{L}{\lambda})

    Args:
        lambda_achterland (float): de spreidingslengte van het achterland [m]
        L_achterland (float): afstand van uittredepunten tot achterlandlengte [m]

    Returns:
        float: geohydrologische weerstand van het achterland [m]
    """
    return lambda_achterland * math.tanh(L_achterland / lambda_achterland)


def calc_W_voorland(
    lambda_voorland: float, 
    L_voorland: float
    ) -> float:
    r"""Berekent de geohydrologische weerstand van het voorland in m

    .. math::

        W = \lambda tanh(\frac{L}{\lambda})

    Args:
        lambda_voorland (float): de spreidingslengte van het voorland [m]
        L_voorland (float): Geometrische voorlandlengte [m]

    Returns:
        float: geohydrologische weerstand van het voorland [m]
    """
    return lambda_voorland * math.tanh(L_voorland / lambda_voorland)


def calc_L_kwelweg(
    L_but: float,
    W_voorland: float
    ) -> float:
    r"""Berekent de kwelweglengte in m
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
    r"""Berekening grenspotentiaal ten opzichte van maaiveldniveau in m

    Args:
        d_deklaag (float): Dikte van de cohesieve deklaag [m]
        gamma_sat_deklaag (float): verzadigd volumegewicht van de deklaag [kN/m3]
        gamma_water (float): volumegewicht van water [kN/m3]

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

    Args:
        phi_exit (float): stijghoogte in het watervoerende zandpakket ter plaatse van uittredepunt in m+NAP
        h_exit (float): niveau bij het uittredepunt [m+NAP]
        d_deklaag (float): deklaagdikte [m]

    Returns:
        float: heave gradient in [-]
    """
    return (phi_exit - h_exit) / d_deklaag

# functie om r_exit te berekenen met behulp van model4a module
def calc_r_exit_model4a(
     kD_wvp: float,
     D_wvp: float,
     c_voorland: float,
     c_achterland: float,
     L_intrede: float,
     L_but: float,
     L_bit: float,
     L_achterland: float,
) -> float:
    # L_voorland uitrekenen met behulp van de functie calc_L_voorland
    L_voorland = calc_L_voorland(L_intrede, L_but)
    # Maak een Model4a object aan met uitgangspunt x_bit = 0.0. Dit betekent
    # dat de lokale x waarde gelijk is aan L_bit.
    # uittredepunten moeten altijd binnendijks van de binnenteenlijn liggen, 
    # # dus x_but moet negatief zijn.
    model4a = Model4a(
        kD=kD_wvp,
        D=D_wvp,
        c1=c_voorland,
        c3=c_achterland,
        L1=L_voorland,
        L3=L_achterland,
        x_but=-1.0*abs(L_but-L_bit),  # x_but moet negatief zijn, x_bit is 0.0
        x_bit=0.0,)  # x_bit is 0.0
    # Bereken de respons bij het uittredepunt
    r_exit, _, _ = model4a.respons(L_bit)
    return r_exit





#r_but en r_bit? staan niet in de Excel
def calc_r_bit(
    W_voorland: float, 
    L_dijk: float, 
    W_achterland: float
    )-> float:
    r"""Calculates response in stationary models at innertoe based on given weights.

    .. math::

        r_{BIT} = \frac{W_{3}}{W_{1} + L_{2} + W_{3}}

    Args:
        W_voorland (float): geohydrologische weerstand van het voorland [m]
        L_dijk (float): dijkzate [m]
        W_achterland (float): geohydrologische weerstand van het achterland [m]

    Returns:
        float: response at inner toe [0.0-1.0]
    """
    return (W_achterland) / (W_voorland + L_dijk + W_achterland)


def calc_r_but(
    W_voorland: float, 
    L_dijk: float, 
    W_achterland: float
    )-> float:
    r"""Calculates response in stationary models at outer toe based on given weights.

    .. math::

        r_{BUT} = \frac{L_{2} + W_{3}}{W_{1} + L_{2} + W_{3}}

    Args:
        W_voorland (float): geohydrologische weerstand van het voorland [m]
        L_dijk (float): dijkzate [m]
        W_achterland (float): geohydrologische weerstand van het achterland [m]

    Returns:
        float: response at outer toe [0.0-1.0]
    """
    return (L_dijk + W_achterland) / (W_voorland + L_dijk + W_achterland)

#TODO klopt de functie calc_r_exit?
def calc_r_exit(
    L_achterland: float,
    L_bit: float,
    lambda_achterland: float,
    r_BIT: float
    ):
    
    r""" berekening van de respons ter plaatse van het uittredepunt
    
    Args:
        L_achterland (float): afstand van uittredepunt tot achterlandlengte [m]
        L_bit (float): afstand van uittredepunt tot binnenteenlijn [m]
        lambda_achterland (float): de spreidingslengte van het achterland [m]
        r_BIT (float): respons bij binnenteenlijn [-]

    Returns:
        float: respons bij uittredepunt [-]
    
    """
    
    respons = (r_BIT * 
         math.sinh((L_achterland - L_bit) / lambda_achterland) / 
         math.sinh(L_achterland / lambda_achterland)
        )
    
    return respons


def calc_phi_exit(
    polderpeil: float, 
    r_exit: float, 
    buitenwaterstand: float
    ) -> float:  # Van respons naar potentiaal
    r"""Berekent de theoretische stijghoogte bij uittredepunten in m+NAP

    .. math::

        \phi_exit(x) = polderpeil + r(x) (buitenwaterstand - polderpeil)

    Args:
        polderpeil (float): polderpeil [m+NAP]
        r_exit (float): Dempingsfactor bij uittredepunten [-]
        buitenwaterstand (float): buitenwaterstand [m+NAP]

    Returns:
        float: Theoretische stijghoogte bij uittredepunten [m+NAP]
    """
    return polderpeil + r_exit * (buitenwaterstand - polderpeil)

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

    Args:
        d70 (float): 70% percentiel van de korrelgrootteverdeling [m]
        D_wvp (float): dikte van het watervoerende pakket [m]
        kD_wvp (float): transmissiviteit van het watervoerende pakket [m2/dag]
        L_kwelweg (float): kwelweglengte in m
        gamma_water (float): volumegewicht van water [kN/m3]
        g (float): Zwaartekrachtversnelling [m/s2]
        v (float): kinematische viscositeit [m2/s]
        theta (float): rolweerstandshoek [graden] 
        eta (float): coefficiënt van White [-]
        d70_m (float): gemiddelde d70 in kleine schaalproeven [m]
        gamma_korrel (float): (schijnbaar) volumegewicht van de zandkorrels onder water [kN/m3]

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
    Fres = (
        eta
        * ((gamma_korrel - gamma_water) / gamma_water)
        * math.tan(theta * math.pi / 180.00)
    )
    # Berekening Fscale
    Fscale = pow(d70 / d70_m, 0.4) * d70_m / pow(k_intr * L_kwelweg, (1.0 / 3.0))
    # Berekening Fgeometry
    if D_wvp == L_kwelweg:
        D_wvp = D_wvp - 0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D_wvp / L_kwelweg, 2.8) - 1.0))
    Fgeom = 0.91 * pow(D_wvp / L_kwelweg, totdemacht)
    return Fres * Fscale * Fgeom * L_kwelweg


###################################################################################
# Z-functies
###################################################################################

def calc_z_h(
    modelfactor_h: float,
    i_c_h: float,
    i_exit: float
    ) -> float:
    r"""Grenstoestandfunctie voor het mechanisme heave
    
    Args:
        modelfactor_h (float): modelfactor voor heave
        i_c_h (float): kritiek verval [m]
        i_exit (float): gereduceerd verval [m]
    
    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave 
    """

    return (modelfactor_h * i_c_h) - i_exit


def calc_z_u(
    modelfactor_u: float,
    dphi_c_u: float,
    phi_exit: float,
    h_exit: float
    ) -> float:
    r"""Grenstoestandfunctie voor het mechanisme opbarsten (uplift)

    Args:
        modelfactor_u (float): modelfactor voor uplift
        dphi_c_u (float): kritiek verval [m]
        phi_exit (float): stijghoogte in het watervoerende zandpakket ter plaatse van uittredepunt [m+NAP]
        h_exit (float): niveau bij het uittredepunt [m+NAP]

    Returns:
        float: Z waarde van de grenstoestandfunctie voor uplift 
    """

    return modelfactor_u * dphi_c_u - (phi_exit - h_exit)

def calc_z_p(
    modelfactor_p: float,
    dh_c: float,
    dh_red: float
    ) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Args:
        modelfactor_p (float): modelfactor voor piping
        dh_c (float): kritiek verval [m]
        dh_red (float): gereduceerd verval [m]

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """

    return (modelfactor_p * dh_c) - dh_red


