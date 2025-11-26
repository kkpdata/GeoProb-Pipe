import pytest


def test_calculation():
    ##

    from probabilistic_library import Alpha

    from geoprob_pipe.calculations.system_calculations.piping_system.dummy_input import (
        DUMMY_INPUT,
    )
    from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import (
        PipingSystemReliabilityCalculation,
    )
    from geoprob_pipe.deterministic.system import DeterministicSystemCalculation

    obj = PipingSystemReliabilityCalculation(system_variable_distributions=DUMMY_INPUT)
    # Run Model with mean values (deterministic):
    det_obj = DeterministicSystemCalculation(input_object=obj)
    print(det_obj.limit_state_results)
    print(det_obj.system_variable_setup_result)

    # Assert deterministic setup values
    assert det_obj.system_variable_setup_result[0] == pytest.approx(
        -1.41805, abs=0.001
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
        # for alpha in design_point.alphas:
        #     alpha: Alpha
        #     print(
        #         f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}"
        #     )
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
        # print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.system_design_point.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert sum_invloedsfactoren == 1.00, (
        f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."
    )
    assert beta == pytest.approx(3.3269854650232067, abs=0.001), (
        f"De systeembreed betrouwbaarheidindex is niet correct berekend: {beta=}"
    )

    ##
