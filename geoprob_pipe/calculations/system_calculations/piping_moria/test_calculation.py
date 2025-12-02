

def test_calculation():

    ##
    from probabilistic_library import Alpha
    from geoprob_pipe.calculations.system_calculations.piping_moria.reliability_calculation import  (
        PipingMORIASystemReliabilityCalculation)
    from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import DUMMY_INPUT

    obj = PipingMORIASystemReliabilityCalculation(
        system_variable_distributions=DUMMY_INPUT,
    )

    # Run prob system
    obj.run()
    assert obj.validation_messages.cnt == 0
    # print(f"{obj.system_design_point.reliability_index=}")
    # for design_point in obj.model_design_points:
    #     print(f"{design_point.reliability_index=}")

    # Check correlation influences result
    obj2 = PipingMORIASystemReliabilityCalculation(
        system_variable_distributions=DUMMY_INPUT,
        system_variable_correlations=[("lambda_voorland", "k_wvp", 0.8)],
    )
    obj2.run()
    assert obj.system_design_point.reliability_index != obj2.system_design_point.reliability_index

    ##

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
