

def test_calculation():
    ##
    import math
    from probabilistic_library import DistributionType, Alpha
    from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import  (
        PipingSystemReliabilityCalculation)
    from geoprob_pipe.deterministic.system import DeterministicSystemCalculation

    obj = PipingSystemReliabilityCalculation(
        system_variable_distributions=[
            {
                "name": "L_achterland",
                "distribution_type": DistributionType.deterministic,
                "mean": 3500.0,
            },
            {
                "name": "c_voorland",
                "distribution_type": DistributionType.log_normal,
                "mean": 10.0,
                "variation": 0.1
            },
            {
                "name": "c_achterland",
                "distribution_type": DistributionType.log_normal,
                "mean": 50.0,
                "variation": 0.1
            },
            {
                "name": "L_intrede",
                "distribution_type": DistributionType.deterministic,
                "mean": 150.0,
            },
            {
                "name": "L_but",
                "distribution_type": DistributionType.deterministic,
                "mean": 65.0,
            },
            {
                "name": "L_bit",
                "distribution_type": DistributionType.deterministic,
                "mean": 20.0,
            },
            {
                "name": "polderpeil",
                "distribution_type": DistributionType.deterministic,
                "mean": 0.0,
            },
            {
                "name": "buitenwaterstand",
                "distribution_type": DistributionType.deterministic,
                "mean": 5.0,
            },  # TODO Nu Must Klein: Unit test uitbreiden/toevoegen met buitenwaterstand als distributie.
            {
                "name": "mv_exit",
                "distribution_type": DistributionType.deterministic,
                "mean": 0.5,
            },
            {
                "name": "top_zand",
                "distribution_type": DistributionType.normal,
                "mean": -3.0,
                "deviation": 0.5
            },
            {
                "name": "kD_wvp",
                "distribution_type": DistributionType.log_normal,
                "mean": 2000.0,
                "variation": 0.35
            },
            {
                "name": "modelfactor_h",
                "distribution_type": DistributionType.log_normal,
                "mean": 1.0,
                "variation": 0.1
            },
            {
                "name": "i_c_h",
                "distribution_type": DistributionType.log_normal,
                "mean": 0.7,
                "variation": 0.15  # TODO: Of is dit de standaard deviatie
            },
            {
                "name": "D_wvp",
                "distribution_type": DistributionType.log_normal,
                "mean": 50,
                "deviation": 1.5
            },
            {
                "name": "modelfactor_u",
                "distribution_type": DistributionType.log_normal,
                "mean": 1.0,
                "variation": 0.1
            },
            {
                "name": "gamma_water",
                "distribution_type": DistributionType.deterministic,
                "mean": 9.81,
            },
            {
                "name": "gamma_sat_deklaag",
                "distribution_type": DistributionType.log_normal,
                "mean": 13.9,
                "variation": 0.05
            },  # TODO Nu Must Klein: In het Openturns voorbeeld heeft deze een derde parameter met waarde 10. Waarvoor?
            {
                "name": "modelfactor_p",
                "distribution_type": DistributionType.log_normal,
                "mean": 1.0,
                "variation": 0.1
            },
            {
                "name": "d70",
                "distribution_type": DistributionType.log_normal,
                "mean": 2.8e-4,
                "variation": 0.15
            },
            {
                "name": "g",
                "distribution_type": DistributionType.deterministic,
                "mean": 9.81,
            },
            {
                "name": "v",
                "distribution_type": DistributionType.deterministic,
                "mean": 0.00000133,
            },
            {
                "name": "theta",
                "distribution_type": DistributionType.deterministic,
                "mean": 37.0,  # Provide in degrees
            },
            {
                "name": "eta",
                "distribution_type": DistributionType.deterministic,
                "mean": 0.25,
            },
            {
                "name": "d70_m",
                "distribution_type": DistributionType.deterministic,
                "mean": 2.08e-4,
            },
            {
                "name": "gamma_korrel",
                "distribution_type": DistributionType.deterministic,
                "mean": 16.5,
            },
            {
                "name": "r_c_deklaag",
                "distribution_type": DistributionType.deterministic,
                "mean": 0.3,
            },
        ]
    )

    # Semi prob with mean:
    det_obj = DeterministicSystemCalculation(input_object=obj)
    print(det_obj.limit_state_results)

    # Run prob system
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

    # TODO Nu Must Middel: Optie toevoegen dat ParallelSystemReliabilityCalculation ook deterministisch word uitgerekend
    #  Dit doen door gemiddelde waarden te gebruiken.
    # TODO Nu Must Middel: Assert toevoegen die piping resultaat unit test


    ##
