from geoprob_pipe.calculations.limit_states.heave_icw_model4a import z_heave
from geoprob_pipe.calculations.limit_states.uplift_icw_model4a import z_uplift
from geoprob_pipe.calculations.limit_states.piping import z_piping


# noinspection PyPep8Naming
def system_variable_setup(
        buitenwaterstand: float, c_achterland: float, c_voorland: float, d70: float, d70_m: float,
        D_wvp: float,  # TODO Later Should Klein: D zit ook in kD_wvp. Dat is dubbelop.
        eta: float, g: float, gamma_korrel: float, gamma_sat_deklaag: float, gamma_water: float, i_c_h: float,
        kD_wvp: float, L_achterland: float, L_bit: float, L_but: float, L_intrede: float, modelfactor_h: float,
        modelfactor_u: float, modelfactor_p: float, mv_exit: float, polderpeil: float, r_c_deklaag: float, theta: float,
        top_zand: float, v: float,
):
    """ Dummy functie waarmee variabele namen worden geïnitieerd.

    Deze staat toe dat je de distributies toevoegt aan de ReliabilityProject voordat je de systeemmodellen toevoegt.
    Je kunt in één keer alle variabelen toevoegen wat de code overzichtelijker maakt. """
    print(
        L_achterland, c_voorland, c_achterland, L_intrede, L_but, L_bit, polderpeil, buitenwaterstand, mv_exit,
        top_zand, kD_wvp, modelfactor_h, i_c_h, D_wvp, modelfactor_u, gamma_water, gamma_sat_deklaag, modelfactor_p,
        d70, g, v, theta, eta, d70_m, gamma_korrel, r_c_deklaag
    )


# noinspection PyPep8Naming
def calc_Z_h(
        L_achterland: float, c_voorland: float, c_achterland: float, L_intrede: float, L_but: float, L_bit: float,
        polderpeil: float, buitenwaterstand: float, mv_exit: float, top_zand: float, kD_wvp: float,
        modelfactor_h: float, i_c_h: float, D_wvp: float,
) -> float:
    r""" Wrapper over de grenstoestandfunctie voor heave zodat deze bruikbaar is voor de Probabilistic Library.

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return z_heave(
        L_achterland=L_achterland, c_voorland=c_voorland, c_achterland=c_achterland, L_intrede=L_intrede,
        L_but=L_but, L_bit=L_bit, polderpeil=polderpeil, buitenwaterstand=buitenwaterstand, mv_exit=mv_exit,
        top_zand=top_zand, kD_wvp=kD_wvp, modelfactor_h=modelfactor_h, i_c_h=i_c_h, D_wvp=D_wvp
    )[0]


# noinspection PyPep8Naming
def calc_Z_u(
        L_achterland: float, c_voorland: float, c_achterland: float, polderpeil: float, buitenwaterstand: float,
        L_intrede: float, L_but: float, L_bit: float, mv_exit: float, top_zand: float, kD_wvp: float,
        modelfactor_u: float, gamma_water: float, gamma_sat_deklaag: float, D_wvp: float,
) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """

    return z_uplift(
        L_achterland=L_achterland, c_voorland=c_voorland, c_achterland=c_achterland, polderpeil=polderpeil,
        buitenwaterstand=buitenwaterstand, L_intrede=L_intrede, L_but=L_but, L_bit=L_bit, mv_exit=mv_exit,
        top_zand=top_zand, kD_wvp=kD_wvp, modelfactor_u=modelfactor_u, gamma_water=gamma_water,
        gamma_sat_deklaag=gamma_sat_deklaag, D_wvp=D_wvp
    )[0]


# noinspection PyPep8Naming
def calc_Z_p(
        c_voorland: float, buitenwaterstand: float, polderpeil: float, mv_exit: float, L_but: float, L_intrede: float,
        modelfactor_p: float, d70: float, D_wvp: float, kD_wvp: float, top_zand: float, gamma_water: float, g: float,
        v: float, theta: float, eta: float, d70_m: float, gamma_korrel: float, r_c_deklaag: float,
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    # TODO Later Should Klein: Waarom zijn alle vaste parameters toegevoegd? Zoals zwaartekracht g. Global maken?
    return z_piping(
        c_voorland=c_voorland, buitenwaterstand=buitenwaterstand, polderpeil=polderpeil, mv_exit=mv_exit,
        L_but=L_but, L_intrede=L_intrede, modelfactor_p=modelfactor_p, d70=d70, D_wvp=D_wvp, kD_wvp=kD_wvp,
        top_zand=top_zand, gamma_water=gamma_water, g=g, v=v, theta=theta, eta=eta, d70_m=d70_m,
        gamma_korrel=gamma_korrel, r_c_deklaag=r_c_deklaag
    )[0]


MODEL_NAMES = {
    calc_Z_h.__name__: "Heave",
    calc_Z_u.__name__: "Uplift",
    calc_Z_p.__name__: "Piping",
}
