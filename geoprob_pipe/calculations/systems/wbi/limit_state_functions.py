from geoprob_pipe.calculations.limit_states.piping_lm import limit_state_wbi as system_variable_setup


# noinspection PyPep8Naming
def calc_Z_u(
        L_kwelweg: float,
        # Boundary condition parameters
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        # Subsoil property parameters
        top_zand: float, r_exit: float, k_wvp: float, D_wvp: float, d70: float,
        gamma_sat_deklaag: float,
        # Model property parameters
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float, modelfactor_ff: float, modelfactor_3d: float,
        modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float, r_c_deklaag: float,
        # Overige parameters
        gamma_water: float,
        # Constants  # TODO: Ombouwen tot globals
        d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float
) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """
    return system_variable_setup(
        L_kwelweg=L_kwelweg, buitenwaterstand=buitenwaterstand, polderpeil=polderpeil, mv_exit=mv_exit,
        top_zand=top_zand, r_exit=r_exit, k_wvp=k_wvp, D_wvp=D_wvp, d70=d70, gamma_sat_deklaag=gamma_sat_deklaag,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, gamma_water=gamma_water,
        d70_m=d70_m, gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
    )[0]


# noinspection PyPep8Naming
def calc_Z_h(
        L_kwelweg: float,
        # Boundary condition parameters
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        # Subsoil property parameters
        top_zand: float, r_exit: float, k_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        # Model property parameters
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float, modelfactor_ff: float, modelfactor_3d: float,
        modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float, r_c_deklaag: float,
        # Overige parameters
        gamma_water: float,
        # Constants  # TODO: Ombouwen tot globals
        d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float
) -> float:
    r""" Wrapper over de grenstoestandfunctie voor heave zodat deze bruikbaar is voor de Probabilistic Library.

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    return system_variable_setup(
        L_kwelweg=L_kwelweg, buitenwaterstand=buitenwaterstand, polderpeil=polderpeil, mv_exit=mv_exit,
        top_zand=top_zand, r_exit=r_exit, k_wvp=k_wvp, D_wvp=D_wvp, d70=d70, gamma_sat_deklaag=gamma_sat_deklaag,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, gamma_water=gamma_water,
        d70_m=d70_m, gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
    )[1]


# noinspection PyPep8Naming
def calc_Z_p(
        L_kwelweg: float,
        # Boundary condition parameters
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        # Subsoil property parameters
        top_zand: float, r_exit: float, k_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        # Model property parameters
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float, modelfactor_ff: float, modelfactor_3d: float,
        modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float, r_c_deklaag: float,
        # Overige parameters
        gamma_water: float,
        # Constants  # TODO: Ombouwen tot globals
        d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme terugschrijdende erosie (piping).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return system_variable_setup(
        L_kwelweg=L_kwelweg, buitenwaterstand=buitenwaterstand, polderpeil=polderpeil, mv_exit=mv_exit,
        top_zand=top_zand, r_exit=r_exit, k_wvp=k_wvp, D_wvp=D_wvp, d70=d70, gamma_sat_deklaag=gamma_sat_deklaag,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, gamma_water=gamma_water,
        d70_m=d70_m, gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
    )[2]



# noinspection PyPep8Naming
def calc_Z_project(
        L_kwelweg: float,
        # Boundary condition parameters
        buitenwaterstand: float, polderpeil: float, mv_exit: float,
        # Subsoil property parameters
        top_zand: float, r_exit: float, k_wvp: float, D_wvp: float, d70: float, gamma_sat_deklaag: float,
        # Model property parameters
        modelfactor_u: float, modelfactor_h: float, modelfactor_p: float, modelfactor_ff: float, modelfactor_3d: float,
        modelfactor_aniso: float, modelfactor_ml: float, i_c_h: float, r_c_deklaag: float,
        # Overige parameters
        gamma_water: float,
        # Constants  # TODO: Ombouwen tot globals
        d70_m: float, gamma_korrel: float, v: float, theta: float, eta: float, g: float
) -> float:
    r"""Grenstoestandfunctie voor het mechanisme piping. Deze grenstoestandfunctie bepaalt de Z waarde 
    op basis van de afzonderlijke Z waarden van de mechanismen uplift, heave en terugschrijdende erosie door
    max(Z_u, Z_h, Z_p).

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """
    return system_variable_setup(
        L_kwelweg=L_kwelweg, buitenwaterstand=buitenwaterstand, polderpeil=polderpeil, mv_exit=mv_exit,
        top_zand=top_zand, r_exit=r_exit, k_wvp=k_wvp, D_wvp=D_wvp, d70=d70, gamma_sat_deklaag=gamma_sat_deklaag,
        modelfactor_u=modelfactor_u, modelfactor_h=modelfactor_h, modelfactor_p=modelfactor_p,
        modelfactor_ff=modelfactor_ff, modelfactor_3d=modelfactor_3d, modelfactor_aniso=modelfactor_aniso,
        modelfactor_ml=modelfactor_ml, i_c_h=i_c_h, r_c_deklaag=r_c_deklaag, gamma_water=gamma_water,
        d70_m=d70_m, gamma_korrel=gamma_korrel, v=v, theta=theta, eta=eta, g=g,
    )[3]


MODEL_NAMES = {
    calc_Z_u.__name__: "Uplift",
    calc_Z_h.__name__: "Heave",
    calc_Z_p.__name__: "Piping",
}
