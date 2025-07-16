

def test_calculation():
    ##
    from probabilistic_library import DistributionType
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
    beta = obj.system_design_point.reliability_index
    print(f"{beta=}")
    ##
