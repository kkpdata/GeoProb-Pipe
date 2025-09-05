from geoprob_pipe.calculations.limit_states.piping import z_piping

z = z_piping(
    c_voorland=10, buitenwaterstand=7.41, polderpeil=2.75, mv_exit=4.8, L_but=18.6, L_intrede=104, modelfactor_p=1.00,
    d70=0.00045, D_wvp=45, kD_wvp=2500, top_zand=-4, gamma_water=9.81, g=9.81, v=1.33E-06, theta=37, eta=0.25,
    d70_m=2.08E-04, gamma_korrel=26, r_c_deklaag=0.3)
