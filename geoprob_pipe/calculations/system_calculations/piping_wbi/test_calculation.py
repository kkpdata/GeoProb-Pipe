import pytest


def test_calculation():
    ##
    from probabilistic_library import Alpha

    from geoprob_pipe.calculations.system_calculations.piping_wbi.dummy_input import (
        PIPING_DUMMY_INPUT,
    )
    from geoprob_pipe.calculations.system_calculations.piping_wbi.reliability_calculation import (
        PipingWBISystemReliabilityCalculation,
    )
    from geoprob_pipe.deterministic.system import DeterministicSystemCalculation

    obj = PipingWBISystemReliabilityCalculation(
        system_variable_distributions=PIPING_DUMMY_INPUT
    )

    det_obj = DeterministicSystemCalculation(input_object=obj)
    print(det_obj.limit_state_results)
    print(det_obj.system_variable_setup_result)

    # Assert deterministic setup values
    # 0= z_u,
    # 1= z_h,
    # 2= z_p,
    # 3= z_combin,
    # 4= h_exit,
    # 5= phi_exit,
    # 6= dphi_c_u,
    # 7= i_exit,
    # 8= dh_c,
    # 9= dh_red

    assert det_obj.system_variable_setup_result[0] == pytest.approx(
        -1.41805, abs=0.001
    )  # z_u
    assert det_obj.system_variable_setup_result[1] == pytest.approx(
        -0.48518, abs=0.001
    )  # z_h
    assert det_obj.system_variable_setup_result[2] == pytest.approx(
        3.69517, abs=0.001
    )  # z_p
    assert det_obj.system_variable_setup_result[6] == pytest.approx(
        2.030071356, abs=0.001
    )  # dphi_c_u
    assert det_obj.system_variable_setup_result[7] == pytest.approx(
        0.98517688, abs=0.001
    )  # i_exit
    assert det_obj.system_variable_setup_result[8] == pytest.approx(
        6.4451739, abs=0.001
    )  # dh_c
    assert det_obj.system_variable_setup_result[9] == pytest.approx(
        2.75, abs=0.001
    )  # dh_red

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

    ##
    assert sum_invloedsfactoren == 1.00, (
        f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."
    )

    assert beta == pytest.approx(2.6981756664952607, abs=0.001), (
        f"De systeembreed betrouwbaarheidindex is niet correct berekend: {beta=}"
    )
    ##
    ##
