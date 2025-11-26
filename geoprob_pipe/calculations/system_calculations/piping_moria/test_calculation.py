import pytest


def test_calculation():
    ##
    from probabilistic_library import Alpha

    from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import (
        PIPING_DUMMY_INPUT,
    )
    from geoprob_pipe.calculations.system_calculations.piping_moria.reliability_calculation import (
        PipingMORIASystemReliabilityCalculation,
    )
    from geoprob_pipe.deterministic.system import DeterministicSystemCalculation

    obj = PipingMORIASystemReliabilityCalculation(
        system_variable_distributions=PIPING_DUMMY_INPUT
    )
    # Run Model with mean values (deterministic):
    det_obj = DeterministicSystemCalculation(input_object=obj)
    print(det_obj.limit_state_results)
    print(det_obj.system_variable_setup_result)

    # Assert deterministic setup values

    #     0= z_u,
    #     1= z_h,
    #     2= z_p,
    #     3= z_combin,
    #     4= h_exit,
    #     5= r_exit,
    #     6= phi_exit,
    #     7= d_deklaag,
    #     8= dphi_c_u,
    #     9= i_exit,
    #     10= L_voorland,
    #     11= W_voorland,
    #     12= L_kwelweg,
    #     13= kD_wvp,
    #     14= dh_c,
    #     15= dh_red,

    assert det_obj.system_variable_setup_result[8] == pytest.approx(
        2.030071356, abs=0.001
    )  # dphi_c_u

    assert det_obj.system_variable_setup_result[5] == pytest.approx(
        0.7896238, abs=0.001
    )  # r_exit

    assert det_obj.system_variable_setup_result[6] == pytest.approx(
        3.95, abs=0.001
    )  # phi_exit

    assert det_obj.system_variable_setup_result[0] == pytest.approx(
        -1.41805, abs=0.01
    )  # z_u
    assert det_obj.system_variable_setup_result[1] == pytest.approx(
        -0.48518, abs=0.001
    )  # z_h
    assert det_obj.system_variable_setup_result[2] == pytest.approx(
        3.69517, abs=0.001
    )  # z_p
    assert det_obj.system_variable_setup_result[3] == pytest.approx(
        3.69517, abs=0.001
    )  # z_combin
    assert det_obj.system_variable_setup_result[4] == 0.5  # h_exit

    # Run prob system
    obj.run()
    assert obj.validation_messages.cnt == 0

    # Model resultaten
    print("\nModellen:")
    for design_point in obj.model_design_points:
        print(f"{design_point.identifier=}")
        print(f"  {design_point.is_converged=}")
        print(f"  {design_point.reliability_index=}")
        for alpha in design_point.alphas:
            alpha: Alpha
            print(
                f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}"
            )
        alphas_values = [alpha.alpha for alpha in design_point.alphas]
        invloedsfactoren = [value * value for value in alphas_values]
        sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
        assert sum_invloedsfactoren == 1.00, (
            f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."
        )

    # Systeem resultaten
    print("\nSysteem:")
    beta = obj.system_design_point.reliability_index
    print(f"  {beta=}")
    for alpha in obj.system_design_point.alphas:
        alpha: Alpha
        print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.system_design_point.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert sum_invloedsfactoren == 1.00, (
        f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."
    )
    assert beta == pytest.approx(2.9017608040690277, abs=0.001), (
        f"De systeembreed betrouwbaarheidindex is niet correct berekend: {beta=}"
    )

    ##
