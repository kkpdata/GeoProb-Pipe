from geoprob_pipe.calculations.limit_states.piping_lm import limit_state_model4a
#
#
# # noinspection PyPep8Naming
# def system_variable_setup(
#         buitenwaterstand: float, c_achterland: float, c_voorland: float, d70: float, d70_m: float,
#         D_wvp: float,  # TODO Later Should Klein: D zit ook in kD_wvp. Dat is dubbelop.
#         eta: float, g: float, gamma_korrel: float, gamma_sat_deklaag: float, gamma_water: float, i_c_h: float,
#         kD_wvp: float, L_achterland: float, L_bit: float, L_but: float, L_intrede: float, modelfactor_h: float,
#         modelfactor_u: float, modelfactor_p: float, mv_exit: float, polderpeil: float, r_c_deklaag: float, theta: float,
#         top_zand: float, v: float,
# ):
#     """ Dummy functie waarmee variabele namen worden geïnitieerd.
#
#     Deze staat toe dat je de distributies toevoegt aan de ReliabilityProject voordat je de systeemmodellen toevoegt.
#     Je kunt in één keer alle variabelen toevoegen wat de code overzichtelijker maakt. """
#     print(
#         L_achterland, c_voorland, c_achterland, L_intrede, L_but, L_bit, polderpeil, buitenwaterstand, mv_exit,
#         top_zand, kD_wvp, modelfactor_h, i_c_h, D_wvp, modelfactor_u, gamma_water, gamma_sat_deklaag, modelfactor_p,
#         d70, g, v, theta, eta, d70_m, gamma_korrel, r_c_deklaag
#     )


# noinspection PyPep8Naming
def calc_Z_u(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float, buitenwaterstand: float, polderpeil: float,
        mv_exit: float, top_zand: float, kD_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        c_voorland: float, c_achterland: float, modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float,
        r_c_deklaag: float, d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """

    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit, L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand, kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland, c_achterland=c_achterland,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m, gamma_korrel=gamma_korrel,
        v=v, theta=theta, eta=eta, g=g, gamma_water=gamma_water)[0]


# noinspection PyPep8Naming
def calc_Z_h(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float, buitenwaterstand: float, polderpeil: float,
        mv_exit: float, top_zand: float, kD_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        c_voorland: float, c_achterland: float, modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float,
        r_c_deklaag: float, d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r""" Wrapper over de grenstoestandfunctie voor heave zodat deze bruikbaar is voor de Probabilistic Library.

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit, L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand, kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland, c_achterland=c_achterland,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m, gamma_korrel=gamma_korrel,
        v=v, theta=theta, eta=eta, g=g, gamma_water=gamma_water)[1]


# noinspection PyPep8Naming
def calc_Z_p(
        L_intrede: float, L_but: float, L_bit: float, L_achterland: float, buitenwaterstand: float, polderpeil: float,
        mv_exit: float, top_zand: float, kD_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        c_voorland: float, c_achterland: float, modelfactor_u: float, modelfactor_h: float, modelfactor_p: float,
        modelfactor_ff: float, modelfactor_3d: float, modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float,
        r_c_deklaag: float, d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float,
        gamma_water: float
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return limit_state_model4a(
        L_intrede=L_intrede, L_but=L_but, L_bit=L_bit, L_achterland=L_achterland, buitenwaterstand=buitenwaterstand,
        polderpeil=polderpeil, mv_exit=mv_exit, top_zand=top_zand, kD_wvp=kD_wvp, D_wvp=D_wvp, d70=d70,
        gamma_sat_deklaag=gamma_sat_deklaag, c_voorland=c_voorland, c_achterland=c_achterland,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, d70_m=d70_m, gamma_korrel=gamma_korrel,
        v=v, theta=theta, eta=eta, g=g, gamma_water=gamma_water)[2]


MODEL_NAMES = {
    calc_Z_h.__name__: "Heave",
    calc_Z_u.__name__: "Uplift",
    calc_Z_p.__name__: "Piping",
}
