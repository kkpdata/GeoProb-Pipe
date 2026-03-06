

def test_calculation():
    # TODO Later Should Klein: Nadenken hoe we binnen een half uur een
    #  quick scan piping kunnen uitvoeren met het object.
    #  Is het daarvoor te complex?

    ##
    from probabilistic_library import Alpha
    from geoprob_pipe.calculations.systems.model4a.reliability_calculation import  (
        Model4aCalculation)
    from geoprob_pipe.calculations.systems.mappers.initial_input_mapper import INITIAL_INPUT_MAPPER
    obj = Model4aCalculation(distributions=INITIAL_INPUT_MAPPER['model4a']['input'])
 
    # Run prob system
    obj.run()

    # Model resultaten
    print(f"\nModellen:")
    for design_point in obj.results.dps_limit_states:
        print(f"{design_point.identifier=}")
        print(f"  {design_point.is_converged=}")
        print(f"  {design_point.reliability_index=}")
        for alpha in design_point.alphas:
            alpha: Alpha
            print(f"  {alpha.variable.name=}, {alpha.alpha=}, "
                  f"{alpha.alpha*alpha.alpha=}")
        alphas_values = [alpha.alpha for alpha in design_point.alphas]
        invloedsfactoren = [value * value for value in alphas_values]
        sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
        assert sum_invloedsfactoren == 1.00, \
            (f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is "
             f"niet gelijk aan aan 1.00.")

    # Systeem resultaten
    print(f"\nSysteem:")
    beta = obj.results.dp_combine.reliability_index
    print(f"  {beta=}")
    for alpha in obj.results.dp_combine.alphas:
        alpha: Alpha
        print(f"  {alpha.variable.name=}, {alpha.alpha=}, "
              f"{alpha.alpha*alpha.alpha=}")
    alphas_values = [alpha.alpha for alpha in obj.results.dp_combine.alphas]
    invloedsfactoren = [value * value for value in alphas_values]
    sum_invloedsfactoren = round(sum(invloedsfactoren), 2)
    assert sum_invloedsfactoren == 1.00, \
        (f"De som van de invloedsfactoren ({sum_invloedsfactoren=}) is niet "
         f"gelijk aan aan 1.00.")

    # TODO Nu Must Middel: Optie toevoegen dat
    #  ParallelSystemReliabilityCalculation ook deterministisch word
    #  uitgerekend
    #  Dit doen door gemiddelde waarden te gebruiken.
    # TODO Nu Must Middel: Assert toevoegen die piping resultaat unit test

    ##
