def test_calculation():
    # TODO Later Should Klein: Nadenken hoe we binnen een half uur een quick scan piping kunnen uitvoeren met het object.
    #  Is het daarvoor te complex?

    ##
    from typing import Dict, cast

    from probabilistic_library import Alpha

    from geoprob_pipe.calculations.system_calculations.piping_system.dummy_input import DUMMY_INPUT
    from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import (
        PipingSystemReliabilityCalculation)
    from geoprob_pipe.deterministic.system import DeterministicSystemCalculation

    obj = PipingSystemReliabilityCalculation(system_variable_distributions=DUMMY_INPUT)
    # Run Model with mean values (deterministic):
    det_obj = DeterministicSystemCalculation(input_object=obj)
    print(det_obj.limit_state_results)
    print(det_obj.system_variable_setup_result)  # TODO <-- Tussenliggende resultaten incl. Z-waarden

    ##

    # TODO: Dit is denk ik verkeerd geïnterpreteerd en werkt zo niet. Zo even bij praten? Groet Chris
    assert det_obj.limit_state_results["d70"] == 3.5e-4
    assert det_obj.limit_state_results["c_voorland"] == 10.0
    assert det_obj.limit_state_results["r_exit"] == 0.7
    assert det_obj.limit_state_results["r_exit"] == 0.7

    # Run prob system
    obj.run()

    # Model resultaten
    print(f"\nModellen:")
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
        assert (
            sum_invloedsfactoren == 1.00
        ), f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."

    # Systeem resultaten
    print(f"\nSysteem:")
    beta = obj.system_design_point.reliability_index
    print(f"  {beta=}")
    for alpha in obj.system_design_point.alphas:
        alpha: Alpha
        # print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.system_design_point.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert (
        sum_invloedsfactoren == 1.00
    ), f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."
    assert (
        beta == 4.24
    ), f"De systeembreed betrouwbaarheidindex is niet correct berekend: {beta=}"

    # TODO Nu Must Middel: Optie toevoegen dat ParallelSystemReliabilityCalculation ook deterministisch word uitgerekend
    #  Dit doen door gemiddelde waarden te gebruiken.
    # TODO Nu Must Middel: Assert toevoegen die piping resultaat unit test

    ##
