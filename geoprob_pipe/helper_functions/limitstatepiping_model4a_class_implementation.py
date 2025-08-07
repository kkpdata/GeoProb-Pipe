"""Python module for the calculation of the limit state function for piping, heave and uplift in a sand layer with a cover layer."""

from dataclasses import dataclass

from geoprob_pipe.helper_functions import geohydro_functions, model4a, piping_functions_old

# Define the input variables for the functions for Uplift, Heave and Piping
# dist_L_geom: float
# dist_BUT: float
# dist_BIT: float
# L3_geom: float
# mv: float
# pp: float
# top_zand: float
# gamma_sat_cover: float
# gamma_w: float
# kD: float
# D: float
# d70: float
# c1: float
# c3: float
# mu: float
# mh: float
# mp: float
# i_c_h: float
# rc: float
# h: float
## Class implementation


@dataclass
class LimitStatePipingModel4a:
    r"""
    Class voor het berekenen van de gecombineerde grenstoestandfunctie voor uplift, heave en piping.
    Gebruikt model 4a potentiaal berekening
    """

    dist_L_geom: float
    dist_BUT: float
    dist_BIT: float
    L3_geom: float
    mv: float
    pp: float
    top_zand: float
    gamma_sat_cover: float
    gamma_w: float
    kD: float
    D: float
    d70: float
    c_1: float
    c_3: float
    mu: float
    mh: float
    mp: float
    i_c_h: float
    rc: float
    h: float

    # noinspection PyPep8Naming
    @property
    def D_cover(self) -> float:
        return piping_functions_old.calc_Dcover(self.mv, self.top_zand)

    @property
    def h_exit(self) -> float:
        return piping_functions_old.calc_h_exit(self.pp, self.mv)

    @property
    def dh_red(self) -> float:
        return piping_functions_old.calc_dH_red(self.h, self.h_exit, self.rc, self.D_cover)

    @property
    def d_pot_c_u(self) -> float:
        return piping_functions_old.calc_d_pot_c_u(
            self.D_cover, self.gamma_sat_cover, self.gamma_w
        )

    @property
    def k(self) -> float:
        return self.kD / self.D

    @property
    def r_exit(self) -> float:
        pot_model = model4a.Model4a(
            kD=self.k * self.D,
            D=self.D,
            c1=self.c_1,
            c3=self.c_3,
            L1=self.dist_L_geom - self.dist_BUT,
            L3=self.L3_geom,
            x_but=(0.0 - (self.dist_BUT - self.dist_BIT)),
            x_bit=0.0,
        )
        r_exit, r_but, r_bit = pot_model.respons(
            self.dist_BIT
        )  # dist_BIT is gebruikt omdat Model4a rekent met een absolute waarde voor de x-coordinate
        return r_exit

    @property
    def pot_exit(self) -> float:
        return geohydro_functions.calc_respons2pot(self.pp, self.r_exit, self.h)

    # noinspection PyPep8Naming
    @property
    def L_kwelweg(self) -> float:
        pot_model = model4a.Model4a(
            kD=self.k * self.D,
            D=self.D,
            c1=self.c_1,
            c3=self.c_3,
            L1=self.dist_L_geom - self.dist_BUT,
            L3=self.L3_geom,
            x_but=(0.0 - (self.dist_BUT - self.dist_BIT)),
            x_bit=0.0,
        )
        return pot_model.W1 + self.dist_BUT

    @property
    def i_optredend(self) -> float:
        return piping_functions_old.calc_i_optredend(
            self.pot_exit, self.h_exit, self.D_cover
        )

    @property
    def dh_c(self) -> float:
        return piping_functions_old.calc_dH_sellmeijer(
            self.d70, self.k, self.D, self.L_kwelweg, self.gamma_w
        )

    # noinspection PyPep8Naming
    @property
    def Z_u(self) -> float:
        return piping_functions_old.calc_Z_u(
            self.d_pot_c_u, self.pot_exit, self.h_exit, self.mu
        )

    # noinspection PyPep8Naming
    @property
    def Z_h(self) -> float:
        return piping_functions_old.calc_Z_h(self.i_c_h, self.i_optredend, self.mh)

    # noinspection PyPep8Naming
    @property
    def Z_p(self) -> float:
        return piping_functions_old.calc_Z_p(self.dh_c, self.dh_red, self.mp)

    # noinspection PyPep8Naming
    @property
    def Z_combin(self) -> float:
        return max(self.Z_u, self.Z_h, self.Z_p)


# noinspection PyPep8Naming
def Z_u(
    dist_L_geom: float,
    dist_BUT: float,
    dist_BIT: float,
    L3_geom: float,
    mv: float,
    pp: float,
    top_zand: float,
    gamma_sat_cover: float,
    gamma_w: float,
    kD: float,
    D: float,
    d70: float,
    c_1: float,
    c_3: float,
    mu: float,
    mh: float,
    mp: float,
    i_c_h: float,
    rc: float,
    h: float,
) -> float:
    """
    Calculate the Z_u value for the given parameters, using the LimitStatePipingModel4a class.
    """
    limit_state = LimitStatePipingModel4a(
        dist_L_geom=dist_L_geom,
        dist_BUT=dist_BUT,
        dist_BIT=dist_BIT,
        L3_geom=L3_geom,
        mv=mv,
        pp=pp,
        top_zand=top_zand,
        gamma_sat_cover=gamma_sat_cover,
        gamma_w=gamma_w,
        kD=kD,
        D=D,
        d70=d70,
        c_1=c_1,
        c_3=c_3,
        mu=mu,
        mh=mh,
        mp=mp,
        i_c_h=i_c_h,
        rc=rc,
        h=h,
    )
    return limit_state.Z_u


# noinspection PyPep8Naming
def Z_h(
    dist_L_geom: float,
    dist_BUT: float,
    dist_BIT: float,
    L3_geom: float,
    mv: float,
    pp: float,
    top_zand: float,
    gamma_sat_cover: float,
    gamma_w: float,
    kD: float,
    D: float,
    d70: float,
    c_1: float,
    c_3: float,
    mu: float,
    mh: float,
    mp: float,
    i_c_h: float,
    rc: float,
    h: float,
) -> float:
    """
    Calculate the Z_h value for the given parameters, using the LimitStatePipingModel4a class.
    """
    limit_state = LimitStatePipingModel4a(
        dist_L_geom=dist_L_geom,
        dist_BUT=dist_BUT,
        dist_BIT=dist_BIT,
        L3_geom=L3_geom,
        mv=mv,
        pp=pp,
        top_zand=top_zand,
        gamma_sat_cover=gamma_sat_cover,
        gamma_w=gamma_w,
        kD=kD,
        D=D,
        d70=d70,
        c_1=c_1,
        c_3=c_3,
        mu=mu,
        mh=mh,
        mp=mp,
        i_c_h=i_c_h,
        rc=rc,
        h=h,
    )
    return limit_state.Z_h


# noinspection PyPep8Naming
def Z_p(
    dist_L_geom: float,
    dist_BUT: float,
    dist_BIT: float,
    L3_geom: float,
    mv: float,
    pp: float,
    top_zand: float,
    gamma_sat_cover: float,
    gamma_w: float,
    kD: float,
    D: float,
    d70: float,
    c_1: float,
    c_3: float,
    mu: float,
    mh: float,
    mp: float,
    i_c_h: float,
    rc: float,
    h: float,
) -> float:
    """
    Calculate the Z_p value for the given parameters, using the LimitStatePipingModel4a class.
    """
    limit_state = LimitStatePipingModel4a(
        dist_L_geom=dist_L_geom,
        dist_BUT=dist_BUT,
        dist_BIT=dist_BIT,
        L3_geom=L3_geom,
        mv=mv,
        pp=pp,
        top_zand=top_zand,
        gamma_sat_cover=gamma_sat_cover,
        gamma_w=gamma_w,
        kD=kD,
        D=D,
        d70=d70,
        c_1=c_1,
        c_3=c_3,
        mu=mu,
        mh=mh,
        mp=mp,
        i_c_h=i_c_h,
        rc=rc,
        h=h,
    )
    return limit_state.Z_p
