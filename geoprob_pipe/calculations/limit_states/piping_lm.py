"""Alternatieve implementatie van de grenstoestandsfuncties voor het WBI-model, model 4a en MORIA. Alle
grenstoestandsfuncties worden gecombineerd in één functie per model. De fysische componenten worden geïmporteerd vanuit
de subpackage `physical_components.piping`. Deze implementatie is bedoeld om de leesbaarheid en onderhoudbaarheid van
de code te verbeteren."""

from typing import Tuple

import geoprob_pipe.calculations.physical_components.piping as pc_piping


# noinspection PyPep8Naming
def limit_state_wbi(
    # Geometry parameters
    L_kwelweg: float,
    # Boundary condition parameters
    buitenwaterstand: float,
    polderpeil: float,
    mv_exit: float,
    # Subsoil property parameters
    top_zand: float,
    r_exit: float,
    k_wvp: float,
    D_wvp: float,
    d70: float,
    gamma_sat_deklaag: float,
    # Model property parameters
    modelfactor_u: float,
    modelfactor_h: float,
    modelfactor_p: float,
    modelfactor_ff: float,
    modelfactor_3d: float,
    modelfactor_aniso: float,
    modelfactor_ml: float,
    i_c_h: float,
    r_c_deklaag: float,
    # Overige parameters
    gamma_water: float,
    # Constants  # TODO: Ombouwen tot globals
    d70_m: float,
    gamma_korrel: float,
    v: float,
    theta: float,
    eta: float,
    g: float,
) -> Tuple[float, float, float, float, float, float, float, float, float, float]:
    """Grenstoestandsfuncties volgens het standaard WBI-model.

    :param L_kwelweg:
    :param buitenwaterstand:
    :param polderpeil:
    :param mv_exit:
    :param top_zand:
    :param r_exit:
    :param k_wvp:
    :param D_wvp:
    :param d70:
    :param gamma_sat_deklaag:
    :param gamma_water:
    :param modelfactor_u:
    :param modelfactor_h:
    :param modelfactor_p:
    :param modelfactor_ff: Model factor fijne fractie
    :param modelfactor_3d: Model factor 3D effecten
    :param modelfactor_aniso: Model factor anisotropie
    :param modelfactor_ml: Model factor meerlaagsheid zandpakket
    :param i_c_h:
    :param r_c_deklaag:
    :param d70_m:
    :param gamma_korrel:
    :param v:
    :param theta:
    :param eta:
    :param g:
    :return:
    """
    # d_deklaag
    d_deklaag = pc_piping.calc_d_deklaag(mv_exit=mv_exit, top_zand=top_zand)

    # phi_exit
    phi_exit = pc_piping.calc_phi_exit(
        polderpeil=polderpeil, r_exit=r_exit, buitenwaterstand=buitenwaterstand
    )
    # h_exit
    h_exit = pc_piping.calc_h_exit(polderpeil=polderpeil, mv_exit=mv_exit)
    # dc_phi_c_u
    dphi_c_u = pc_piping.calc_dphi_c_u(
        d_deklaag=d_deklaag,
        gamma_sat_deklaag=gamma_sat_deklaag,
        gamma_water=gamma_water,
    )
    # i_exit
    i_exit = pc_piping.calc_i_exit(
        phi_exit=phi_exit, h_exit=h_exit, d_deklaag=d_deklaag
    )
    # dh_c
    dh_c = pc_piping.calc_dh_c(
        d70=d70,
        D_wvp=D_wvp,
        kD_wvp=k_wvp * D_wvp,
        L_kwelweg=L_kwelweg,
        gamma_water=gamma_water,
        g=g,
        v=v,
        theta=theta,
        eta=eta,
        d70_m=d70_m,
        gamma_korrel=gamma_korrel,
    )
    # dh_red
    dh_red = pc_piping.calc_dh_red(
        buitenwaterstand=buitenwaterstand,
        h_exit=h_exit,
        r_c_deklaag=r_c_deklaag,
        d_deklaag=d_deklaag,
    )
    # z_u
    z_u = modelfactor_u * dphi_c_u - (phi_exit - h_exit)
    # z_h
    z_h = (modelfactor_h * i_c_h) - i_exit
    # z_p
    z_p = (
        modelfactor_p
        * modelfactor_ff
        * modelfactor_3d
        * modelfactor_aniso
        * modelfactor_ml
        * dh_c
    ) - dh_red
    # z_combin
    z_combin = max(z_u, z_h, z_p)

    return z_u, z_h, z_p, z_combin, h_exit, phi_exit, dphi_c_u, i_exit, dh_c, dh_red


# Define the input variables for the model4 limit state
# The variables are grouped into categories for clarity
# --geometry--
# L_intrede: float
# L_but: float
# L_bit: float
# L_achterland: float
# --Boundary conditions--
# buitenwaterstand: float
# polderpeil: float
# mv_exit: float
# --subsoil properties--
# top_zand: float
# kD_wvp: float
# D_wvp: float
# d70: float
# gamma_sat_deklaag: float
# c_voorland: float
# c_achterland: float
# --model properties--
# modelfactor_u: float
# modelfactor_h: float
# modelfactor_p: float
# modelfactor_ff: float model factor fijne fractie
# modelfactor_3d: float model factor 3D effecten
# modelfactor_aniso: float model factor anisotropie
# modelfactor_ml: float model factor meerlaagsheid zandpakket
# i_c_h: float
# r_c_deklaag: float
# d70_m: float
# gamma_korrel: float
# v: float
# theta: float
# eta: float
# --constants--
# g: float
# gamma_water: float


# noinspection PyPep8Naming
def limit_state_model4a(
    L_intrede: float,
    L_but: float,
    L_bit: float,
    L_achterland: float,
    buitenwaterstand: float,
    polderpeil: float,
    mv_exit: float,
    top_zand: float,
    kD_wvp: float,
    D_wvp: float,
    d70: float,
    gamma_sat_deklaag: float,
    c_voorland: float,
    c_achterland: float,
    modelfactor_u: float,
    modelfactor_h: float,
    modelfactor_p: float,
    modelfactor_ff: float,
    modelfactor_3d: float,
    modelfactor_aniso: float,
    modelfactor_ml: float,
    i_c_h: float,
    r_c_deklaag: float,
    d70_m: float,
    gamma_korrel: float,
    v: float,
    theta: float,
    eta: float,
    g: float,
    gamma_water: float,
    **_,
) -> Tuple[
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
]:
    """Grenstoestandsfuncties volgens het WBI-model met grondwaterstroming conform model 4a."""
    # L_voorland
    L_voorland = pc_piping.calc_lengte_voorland(L_intrede=L_intrede, L_but=L_but)
    # lambda_voorland
    lambda_voorland = pc_piping.calc_lambda_voorland(
        kD_wvp=kD_wvp, c_voorland=c_voorland
    )
    # W_voorland of effectieve voorlandlengte
    W_voorland = pc_piping.calc_W_voorland(
        lambda_voorland=lambda_voorland, L_voorland=L_voorland
    )
    # L_kwelweg
    L_kwelweg = pc_piping.calc_L_kwelweg(L_but=L_but, W_voorland=W_voorland)
    # h_exit
    h_exit = pc_piping.calc_h_exit(polderpeil=polderpeil, mv_exit=mv_exit)

    # r_exit
    r_exit = pc_piping.calc_r_exit_model4a(
        kD_wvp=kD_wvp,
        D_wvp=D_wvp,
        c_voorland=c_voorland,
        c_achterland=c_achterland,
        L_but=L_but,
        L_bit=L_bit,
        L_achterland=L_achterland,
        L_voorland=L_voorland,
    )
    # d_deklaag
    d_deklaag = pc_piping.calc_d_deklaag(mv_exit=mv_exit, top_zand=top_zand)

    # phi_exit
    phi_exit = pc_piping.calc_phi_exit(
        polderpeil=polderpeil, r_exit=r_exit, buitenwaterstand=buitenwaterstand
    )
    # dc_phi_c_u
    dphi_c_u = pc_piping.calc_dphi_c_u(
        d_deklaag=d_deklaag,
        gamma_sat_deklaag=gamma_sat_deklaag,
        gamma_water=gamma_water,
    )
    # i_exit
    i_exit = pc_piping.calc_i_exit(
        phi_exit=phi_exit, h_exit=h_exit, d_deklaag=d_deklaag
    )
    # dh_c
    dh_c = pc_piping.calc_dh_c(
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
        gamma_korrel=gamma_korrel,
    )
    # dh_red
    dh_red = pc_piping.calc_dh_red(
        buitenwaterstand=buitenwaterstand,
        h_exit=h_exit,
        r_c_deklaag=r_c_deklaag,
        d_deklaag=d_deklaag,
    )
    # z_u
    z_u = modelfactor_u * dphi_c_u - (phi_exit - h_exit)
    # z_h
    z_h = (modelfactor_h * i_c_h) - i_exit
    # z_p
    z_p = (
        modelfactor_p
        * modelfactor_ff
        * modelfactor_3d
        * modelfactor_aniso
        * modelfactor_ml
        * dh_c
    ) - dh_red
    # z_combin
    z_combin = max(z_u, z_h, z_p)

    return (
        z_u,
        z_h,
        z_p,
        z_combin,
        h_exit,
        r_exit,
        phi_exit,
        d_deklaag,
        dphi_c_u,
        i_exit,
        L_voorland,
        lambda_voorland,
        W_voorland,
        L_kwelweg,
        dh_c,
        dh_red,
    )


# noinspection PyPep8Naming
def limit_state_moria(  # TODO: Naam moria vervangen voor iets generieks? --> limit_state_gw_flow_model?
    # Geometry parameters
    L_intrede: float,
    L_but: float,  # TODO: Moet L_but L_buk worden? Of L_spreidingslengte?
    # Boundary condition parameters
    buitenwaterstand: float,
    buitenwaterstand_gemiddeld: float,
    polderpeil: float,
    mv_exit: float,
    # Subsoil property parameters
    lambda_voorland: float,
    phi_exit_gemiddeld: float,
    r_exit: float,
    top_zand: float,
    k_wvp: float,
    D_wvp: float,
    d70: float,
    gamma_sat_deklaag: float,
    # Model property parameters
    modelfactor_u: float,
    modelfactor_h: float,
    modelfactor_p: float,
    modelfactor_ff: float,
    modelfactor_3d: float,
    modelfactor_aniso: float,
    modelfactor_ml: float,
    i_c_h: float,
    r_c_deklaag: float,
    d70_m: float,
    gamma_korrel: float,
    v: float,
    theta: float,
    eta: float,
    # Constants
    g: float,
    gamma_water: float,
) -> Tuple[
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
]:
    """Grenstoestandsfuncties volgens het WBI-model met grondwaterstroming conform MORIA model.

    :param L_intrede:
    :param L_but:
    :param buitenwaterstand:
    :param buitenwaterstand_gemiddeld:
    :param polderpeil:
    :param mv_exit:
    :param lambda_voorland:
    :param phi_exit_gemiddeld:
    :param r_exit:
    :param top_zand:
    :param k_wvp:
    :param D_wvp:
    :param d70:
    :param gamma_sat_deklaag:
    :param modelfactor_u:
    :param modelfactor_h:
    :param modelfactor_p:
    :param modelfactor_ff: Model factor fijne fractie.
    :param modelfactor_3d: Model factor 3D effecten.
    :param modelfactor_aniso: Model factor anisotropie.
    :param modelfactor_ml: Model factor meerlaagsheid zandpakket.
    :param i_c_h:
    :param r_c_deklaag:
    :param d70_m:
    :param gamma_korrel:
    :param v:
    :param theta:
    :param eta:
    :param g:
    :param gamma_water:
    :return:
    """

    # kD_wvp
    kD_wvp = k_wvp * D_wvp
    # L_voorland
    L_voorland = pc_piping.calc_lengte_voorland(L_intrede=L_intrede, L_but=L_but)
    # W_voorland of effectieve voorlandlengte
    W_voorland = pc_piping.calc_W_voorland(
        lambda_voorland=lambda_voorland, L_voorland=L_voorland
    )
    # L_kwelweg
    L_kwelweg = pc_piping.calc_L_kwelweg(L_but=L_but, W_voorland=W_voorland)
    # h_exit
    h_exit = pc_piping.calc_h_exit(polderpeil=polderpeil, mv_exit=mv_exit)

    # d_deklaag
    d_deklaag = pc_piping.calc_d_deklaag(mv_exit=mv_exit, top_zand=top_zand)

    # phi_exit
    phi_exit = (
        r_exit * (buitenwaterstand - buitenwaterstand_gemiddeld) + phi_exit_gemiddeld
    )
    # dc_phi_c_u
    dphi_c_u = pc_piping.calc_dphi_c_u(
        d_deklaag=d_deklaag,
        gamma_sat_deklaag=gamma_sat_deklaag,
        gamma_water=gamma_water,
    )
    # i_exit
    i_exit = pc_piping.calc_i_exit(
        phi_exit=phi_exit, h_exit=h_exit, d_deklaag=d_deklaag
    )
    # dh_c
    dh_c = pc_piping.calc_dh_c(
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
        gamma_korrel=gamma_korrel,
    )
    # dh_red
    dh_red = pc_piping.calc_dh_red(
        buitenwaterstand=buitenwaterstand,
        h_exit=h_exit,
        r_c_deklaag=r_c_deklaag,
        d_deklaag=d_deklaag,
    )
    # z_u
    z_u = modelfactor_u * dphi_c_u - (phi_exit - h_exit)
    # z_h
    z_h = (modelfactor_h * i_c_h) - i_exit
    # z_p
    z_p = (
        modelfactor_p
        * modelfactor_ff
        * modelfactor_3d
        * modelfactor_aniso
        * modelfactor_ml
        * dh_c
    ) - dh_red
    # z_combin
    z_combin = max(z_u, z_h, z_p)

    return (
        z_u,
        z_h,
        z_p,
        z_combin,
        h_exit,
        r_exit,
        phi_exit,
        d_deklaag,
        dphi_c_u,
        i_exit,
        L_voorland,
        W_voorland,
        L_kwelweg,
        kD_wvp,
        dh_c,
        dh_red,
    )
