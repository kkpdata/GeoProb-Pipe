

def test_calculation():

    ##
    from probabilistic_library import Alpha
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import SystemCalculation
    from geoprob_pipe.calculations.systems.moria.reliability_calculation import  (
        MORIACalculation)
    from geoprob_pipe.calculations.systems.moria.initial_input import (
        INITIAL_INPUT)

    obj: SystemCalculation = MORIACalculation(distributions=INITIAL_INPUT)

    # Run prob system
    obj.run()
    assert obj.validation_messages.cnt == 0

    # Model resultaten
    print(f"\nModellen:")
    for design_point in obj.results.dps_limit_states:
        print(f"{design_point.identifier=}")
        print(f"  {design_point.is_converged=}")
        print(f"  {design_point.reliability_index=}")
        for alpha in design_point.alphas:
            alpha: Alpha
            print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
        alphas_values = [alpha.alpha for alpha in design_point.alphas]
        invloedsfactoren = [value * value for value in alphas_values]
        sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
        assert sum_invloedsfactoren == 1.00, \
            f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."

    # Systeem resultaten
    print(f"\nSysteem:")
    beta = obj.results.dp_combine.reliability_index
    print(f"  {beta=}")
    for alpha in obj.results.dp_combine.alphas:
        alpha: Alpha
        print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.results.dp_combine.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert sum_invloedsfactoren == 1.00, \
        f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."

    ##
