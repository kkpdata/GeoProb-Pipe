import piping_functions_nieuw as piping_functions


#TODO
#noem dit anders
def uitvoeringsfunctie_z_h(
    vak, 
    uittredepunt, 
    ondergrondscenario,
    constanten
    ) -> float:  
    r"""Berekening van de grenstoesstandfunctie voor heave

    Returns:
        float: Z waarde van de grenstoestandfunctie voor heave
    """
    L_achterland = vak.L_achterland
    c_voorland = vak.c_voorland
    c_achterland = vak.c_achterland
    L_intrede = uittredepunt.L_intrede
    L_but = uittredepunt.L_but
    L_bit = uittredepunt.L_bit
    polderpeil = uittredepunt.polderpeil
    buitenwaterstand = uittredepunt.buitenwaterstand
    mv_exit = uittredepunt.mv_exit
    top_zand = ondergrondscenario.top_zand
    kD = ondergrondscenario.kD
    modelfactor_h = constanten.modelfactor_h
    i_c_h = constanten.i_c_h    
        
    L_voorland = piping_functions.calc_L_voorland(
        L_intrede = L_intrede,
        L_but = L_but,
    )

    L_dijk = piping_functions.calc_L_dijk(
        L_bit = L_bit,
        L_but = L_but
    )    
    
    lambda_voorland = piping_functions.calc_lambda_voorland(
        kD = kD,
        c_voorland = c_voorland
    )
    
    lambda_achterland = piping_functions.calc_lambda_achterland(
        kD = kD,
        c_achterland = c_achterland
    )

    W_voorland = piping_functions.calc_W_voorland(
        lambda_voorland = lambda_voorland,
        L_voorland = L_voorland
    )

    W_achteland = piping_functions.calc_W_achterland(
        lambda_achterland = lambda_achterland,
        L_achterland = L_achterland
    )

    r_bit = piping_functions.calc_r_bit(
        W_voorland = W_voorland,
        L_dijk = L_dijk,
        W_achterland = W_achteland
    )

    r_but = piping_functions.calc_r_but(
        W_voorland = W_voorland,
        L_dijk = L_dijk,
        W_achterland = W_achteland
    )

    r_exit = piping_functions.calc_r_exit(
        L_voorland = L_voorland,
        L_achterland = L_achterland,
        L_dijk = L_dijk,
        L_intrede= L_intrede,
        r_bit = r_bit,
        r_but = r_but,
        lambda_achterland = lambda_achterland 
    )       
           
    phi_exit = piping_functions.calc_phi_exit(
        polderpeil = polderpeil,
        r_exit = r_exit,
        buitenwaterstand = buitenwaterstand
    )

    h_exit = piping_functions.calc_h_exit(
        polderpeil = polderpeil,
        mv_exit = mv_exit
    )

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit = mv_exit,
        top_zand = top_zand
    )
  
    i_exit = piping_functions.calc_i_exit(
                phi_exit = phi_exit,
                h_exit = h_exit,
                d_deklaag = d_deklaag
    )

    z_h = piping_functions.calc_z_h(
                i_c_h = i_c_h,
                i_exit = i_exit,
                modelfactor_h = modelfactor_h
    ) 

    return z_h


def calc_Z_u(
    vak, 
    uittredepunt, 
    ondergrondscenario,
    constanten
    ) -> float:
    r"""Grenstoestandfunctie voor opbarsten (uplift).
    
    Returns:
        float: Z waarde van de grenstoestandfunctie voor opbarsten
    """
    
    L_achterland = vak.L_achterland
    c_voorland = vak.c_voorland
    c_achterland = vak.c_achterland
    polderpeil = uittredepunt.polderpeil
    buitenwaterstand = uittredepunt.buitenwaterstand
    L_intrede = uittredepunt.L_intrede
    L_but = uittredepunt.L_but
    L_bit = uittredepunt.L_bit
    mv_exit = uittredepunt.mv_exit
    top_zand = ondergrondscenario.top_zand
    kD_wvp = ondergrondscenario.kD_wvp
    modelfactor_u = constanten.modelfactor_u    
    gamma_w = constanten.gamma_w
    gamma_sat_deklaag = constanten.gamma_sat_deklaag  

    L_voorland = piping_functions.calc_L_voorland(
        L_intrede = L_intrede,
        L_but = L_but,
    )

    L_dijk = piping_functions.calc_L_dijk(
        L_bit = L_bit,
        L_but = L_but
    )

    lambda_voorland = piping_functions.calc_lambda_voorland(
        kD_wvp = kD_wvp,
        c_voorland = c_voorland
    )
    
    lambda_achterland = piping_functions.calc_lambda_achterland(
        kD_wvp = kD_wvp,
        c_achterland = c_achterland
    )

    W_voorland = piping_functions.calc_W_voorland(
        lambda_voorland = lambda_voorland,
        L_voorland = L_voorland
    )

    W_achteland = piping_functions.calc_W_achterland(
        lambda_achterland = lambda_achterland,
        L_achterland = L_achterland
    )

    r_bit = piping_functions.calc_r_bit(
        W_voorland = W_voorland,
        L_dijk = L_dijk,
        W_achterland = W_achteland
    )

    r_but = piping_functions.calc_r_but(
        W_voorland = W_voorland,
        L_dijk = L_dijk,
        W_achterland = W_achteland
    )

    r_exit = piping_functions.calc_r_exit(
        L_voorland = L_voorland,
        L_achterland = L_achterland,
        L_dijk = L_dijk,
        L_intrede= L_intrede,
        r_bit = r_bit,
        r_but = r_but,
        lambda_achterland = lambda_achterland 
    )       

    phi_exit = piping_functions.calc_phi_exit(
        polderpeil = polderpeil,
        r_exit = r_exit,
        buitenwaterstand = buitenwaterstand
    )

    h_exit = piping_functions.calc_h_exit(
        polderpeil = polderpeil,
        mv_exit = mv_exit,
    )

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit= mv_exit,
        top_zand = top_zand
    )

    dphi_c_u = piping_functions.calc_dphi_c_u(
        d_deklaag = d_deklaag,
        gamma_sat_deklaag = gamma_sat_deklaag,
        gamma_w = gamma_w
    )

    z_u = piping_functions.calc_z_u(
        dphi_c_u = dphi_c_u,
        phi_exit = phi_exit,
        h_exit = h_exit,
        modelfactor_u = modelfactor_u
    )

    return z_u


def calc_Z_p(
    vak, 
    uittredepunt, 
    ondergrondscenario,
    constanten
    ) -> float:
    
    r"""Grenstoestandfunctie voor het mechanisme piping

    Returns:
        float: Z waarde van de grenstoestandfunctie voor piping
    """

    c_voorland = vak.c_voorland
    buitenwaterstand = uittredepunt.buitenwaterstand
    polderpeil = uittredepunt.polderpeil
    mv_exit = uittredepunt.mv_exit
    L_but = uittredepunt.L_but
    L_intrede = uittredepunt.L_intrede
    modelfactor_p = ondergrondscenario.modelfactor_p
    d70 = ondergrondscenario.d70
    D_wvp = ondergrondscenario.D_wvp
    kD_wvp = ondergrondscenario.kD_wvp
    top_zand = ondergrondscenario.top_zand
    gamma_water = constanten.gamma_water
    g = constanten.g
    v = constanten.v  
    theta = constanten.theta 
    eta = constanten.eta
    d70_m = constanten.d70_m
    gamma_korrel = constanten.gamma_korrel
    r_c_deklaag = constanten.r_c_deklaag
    
    L_voorland = piping_functions.calc_L_voorland(
        L_intrede = L_intrede,
        L_but = L_but,
    )

    lambda_voorland = piping_functions.calc_lambda_voorland(
        kD_wvp = kD_wvp,
        c_voorland = c_voorland
    )    

    W_voorland = piping_functions.calc_W_voorland(
        lambda_voorland = lambda_voorland,
        L_voorland = L_voorland
    )

    L_kwelweg = piping_functions.calc_L_kwelweg(
        L_but = L_but,
        W_voorland = W_voorland
    )
    
    dh_c = piping_functions.calc_dh_c(
        d70 = d70,
        D_wvp = D_wvp,
        kD_wvp = kD_wvp,
        L_kwelweg = L_kwelweg,
        gamma_water = gamma_water,
        g = g,
        v = v,
        theta = theta,
        eta = eta,
        d70_m = d70_m,
        gamma_korrel = gamma_korrel
    )

    h_exit = piping_functions.calc_h_exit(
        polderpeil = polderpeil,
        mv_exit = mv_exit
    )

    d_deklaag = piping_functions.calc_d_deklaag(
        mv_exit = mv_exit,
        top_zand = top_zand
    )

    dh_red = piping_functions.calc_dh_red(
        buitenwaterstand = buitenwaterstand,
        h_exit = h_exit,
        r_c_deklaag = r_c_deklaag,
        d_deklaag = d_deklaag
    )
    z_p = piping_functions.calc_z_p(
        dh_c = dh_c,
        dh_red = dh_red,
        modelfactor_p = modelfactor_p
    )

    return z_p