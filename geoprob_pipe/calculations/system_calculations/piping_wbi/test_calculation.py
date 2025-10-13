

def test_calculation():

    ##
    from probabilistic_library import Alpha
    from geoprob_pipe.calculations.system_calculations.piping_wbi.reliability_calculation import  (
        PipingWBISystemReliabilityCalculation)
    from geoprob_pipe.calculations.system_calculations.piping_wbi.dummy_input import PIPING_DUMMY_INPUT

    obj = PipingWBISystemReliabilityCalculation(system_variable_distributions=PIPING_DUMMY_INPUT)

    # Run prob system
    obj.run()
    assert obj.validation_messages.cnt == 0

    # Model resultaten
    print(f"\nModellen:")
    for design_point in obj.model_design_points:
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
    beta = obj.system_design_point.reliability_index
    print(f"  {beta=}")
    for alpha in obj.system_design_point.alphas:
        alpha: Alpha
        print(f"  {alpha.variable.name=}, {alpha.alpha=}, {alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.system_design_point.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert sum_invloedsfactoren == 1.00, \
        f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet gelijk aan aan 1.00."

    ##
