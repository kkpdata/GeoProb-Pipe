

def test_calculation():
    ##
    from probabilistic_library import DistributionType, Alpha
    from geoprob_pipe.calculations.system_calculations.example_parallel_system.reliability_calculation import (
        ExampleParallelSystemReliabilityCalculation)

    obj = ExampleParallelSystemReliabilityCalculation(
        system_variable_distributions=[
            {
                "name": "a",
                "distribution_type": DistributionType.uniform,
                "minimum": -1,
                "maximum": 1
            },
            {
                "name": "b",
                "distribution_type": DistributionType.uniform,
                "minimum": -1,
                "maximum": 1
            },
            {
                "name": "c",
                "distribution_type": DistributionType.normal,
                "mean": 0.1,
                "deviation": 0.8
            },
        ]
    )
    obj.run()

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
