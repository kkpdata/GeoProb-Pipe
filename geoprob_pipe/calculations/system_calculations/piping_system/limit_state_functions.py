import geoprob_pipe.helper_functions.piping_functions as piping_functions


# noinspection PyPep8Naming
def system_variable_setup(
        buitenwaterstand: float,
        c_achterland: float,
        c_voorland: float,
        d70: float,
        d70_m: float,
        D_wvp: float,  # TODO Later Should Klein: D zit ook in kD_wvp. Dat is dubbelop.
        eta: float,
        g: float,
        gamma_korrel: float,
        gamma_sat_deklaag: float,
        gamma_water: float,
        # gws_m_mv missing TODO: Waarom in input Excel? Maar is het erg?
        i_c_h: float,
        # k_v_boven_gws missing TODO: Waarom in input Excel? Maar is het erg?
        # k_v_onder_gws missing TODO: Waarom in input Excel? Maar is het erg?
        kD_wvp: float,
        L_achterland: float,
        L_bit: float,
        L_but: float,
        L_intrede: float,
        modelfactor_h: float,
        modelfactor_u: float,
        modelfactor_p: float,
        # mv_achterland_vak
        mv_exit: float,
        # ondergrondscenario_kans missing TODO: Waarom in input Excel? Maar is het erg?
        polderpeil: float,
        r_c_deklaag: float,
        theta: float,
        top_zand: float,
        v: float,
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
        L_achterland: float,
        c_voorland: float,
        c_achterland: float,
        L_intrede: float,
        L_but: float,
        L_bit: float,
        polderpeil: float,
        buitenwaterstand: float,
        mv_exit: float,
        top_zand: float,
        kD_wvp: float,
        modelfactor_h: float,
        i_c_h: float,
        D_wvp: float,
) -> float:
    r"""Berekening van de grenstoestandfunctie voor heave

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """

    L_voorland = piping_functions.calc_L_voorland(
        L_intrede=L_intrede,
        L_but=L_but,
    )

    r_exit = piping_functions.calc_r_exit_model4a(
        kD_wvp=kD_wvp,
        D_wvp=D_wvp,
        c_voorland=c_voorland,
        c_achterland=c_achterland,
        L_but=L_but,
        L_bit=L_bit,
        L_achterland=L_achterland,
        L_voorland=L_voorland
    )

    phi_exit = piping_functions.calc_phi_exit(
        polderpeil=polderpeil,
        r_exit=r_exit,
        buitenwaterstand=buitenwaterstand
    )

    h_exit = piping_functions.calc_h_exit(
        polderpeil=polderpeil,
        mv_exit=mv_exit
    )

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit=mv_exit,
        top_zand=top_zand
    )

    i_exit = piping_functions.calc_i_exit(
        phi_exit=phi_exit,
        h_exit=h_exit,
        d_deklaag=d_deklaag
    )

    z_h = piping_functions.calc_z_h(
        i_c_h=i_c_h,
        i_exit=i_exit,
        modelfactor_h=modelfactor_h
    )

    return z_h


# noinspection PyPep8Naming
def calc_Z_u(
        L_achterland: float,
        c_voorland: float,
        c_achterland: float,
        polderpeil: float,
        buitenwaterstand: float,
        L_intrede: float,
        L_but: float,
        L_bit: float,
        mv_exit: float,
        top_zand: float,
        kD_wvp: float,
        modelfactor_u: float,
        gamma_water: float,
        gamma_sat_deklaag: float,
        D_wvp: float,
) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """

    L_voorland = piping_functions.calc_L_voorland(
        L_intrede=L_intrede,
        L_but=L_but,
    )

    r_exit = piping_functions.calc_r_exit_model4a(
        kD_wvp=kD_wvp,
        D_wvp=D_wvp,
        c_voorland=c_voorland,
        c_achterland=c_achterland,
        L_but=L_but,
        L_bit=L_bit,
        L_achterland=L_achterland,
        L_voorland=L_voorland
    )

    phi_exit = piping_functions.calc_phi_exit(
        polderpeil=polderpeil,
        r_exit=r_exit,
        buitenwaterstand=buitenwaterstand
    )

    h_exit = piping_functions.calc_h_exit(
        polderpeil=polderpeil,
        mv_exit=mv_exit,
    )

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit=mv_exit,
        top_zand=top_zand
    )

    dphi_c_u = piping_functions.calc_dphi_c_u(
        d_deklaag=d_deklaag,
        gamma_sat_deklaag=gamma_sat_deklaag,
        gamma_water=gamma_water
    )

    z_u = piping_functions.calc_z_u(
        dphi_c_u=dphi_c_u,
        phi_exit=phi_exit,
        h_exit=h_exit,
        modelfactor_u=modelfactor_u
    )

    return z_u


# noinspection PyPep8Naming
def calc_Z_p(
        c_voorland: float,
        buitenwaterstand: float,
        polderpeil: float,
        mv_exit: float,
        L_but: float,
        L_intrede: float,
        modelfactor_p: float,
        d70: float,
        D_wvp: float,
        kD_wvp: float,
        top_zand: float,
        gamma_water: float,
        g: float,
        v: float,
        theta: float,
        eta: float,
        d70_m: float,
        gamma_korrel: float,
        r_c_deklaag: float,
        sterkte_factor_fijne_fractie: float,
) -> float:
    """ Grenstoestandfunctie voor het mechanisme piping

    :param c_voorland:
    :param buitenwaterstand:
    :param polderpeil:
    :param mv_exit:
    :param L_but:
    :param L_intrede:
    :param modelfactor_p:
    :param d70:
    :param D_wvp:
    :param kD_wvp:
    :param top_zand:
    :param gamma_water:
    :param g:
    :param v:
    :param theta:
    :param eta:
    :param d70_m:
    :param gamma_korrel:
    :param r_c_deklaag:
    :return: Z waarde van de grenstoestandfunctie voor piping
    :param sterkte_factor_fijne_fractie: Omdat
    """

    L_voorland = piping_functions.calc_L_voorland(
        L_intrede=L_intrede,
        L_but=L_but)

    lambda_voorland = piping_functions.calc_lambda_voorland(
        kD_wvp=kD_wvp,
        c_voorland=c_voorland)

    W_voorland = piping_functions.calc_W_voorland(
        lambda_voorland=lambda_voorland,
        L_voorland=L_voorland)

    L_kwelweg = piping_functions.calc_L_kwelweg(
        L_but=L_but,
        W_voorland=W_voorland)

    dh_c = piping_functions.calc_dh_c(
        d70=d70,
        D_wvp=D_wvp,
        kD_wvp=kD_wvp,
        L_kwelweg=L_kwelweg,
        gamma_water=gamma_water,
        g=g,
        v=v,
        theta=theta,
        eta=eta,
        d70_m=d70_m,
        gamma_korrel=gamma_korrel)

    h_exit = piping_functions.calc_h_exit(
        polderpeil=polderpeil,
        mv_exit=mv_exit)

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit=mv_exit,
        top_zand=top_zand)

    dh_red = piping_functions.calc_dh_red(
        buitenwaterstand=buitenwaterstand,
        h_exit=h_exit,
        r_c_deklaag=r_c_deklaag,
        d_deklaag=d_deklaag)

    z_p = piping_functions.calc_z_p(
        dh_c=dh_c,
        dh_red=dh_red,
        modelfactor_p=modelfactor_p)

    return z_p


MODEL_NAMES = {
    calc_Z_h.__name__: "Heave",
    calc_Z_u.__name__: "Uplift",
    calc_Z_p.__name__: "Piping",
}
