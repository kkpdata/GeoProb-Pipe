# TODO Nu Should Groot: Zou goed zijn om in GeoProb-Pipe voorbeelden op te nemen die tonen dat de applicatie klopt.


class DummyReliabilityCalculation:

    @staticmethod
    def prob_lib_beta() -> float:
        from probabilistic_library import ReliabilityProject, ReliabilityMethod, DistributionType
        from geoprob_pipe.calculations.system_calculations.example_parallel_system.limit_state_functions import (
            limit_state_example_1)

        project = ReliabilityProject()
        project.settings.reliability_method = ReliabilityMethod.form
        project.settings.variation_coefficient = 0.02
        project.settings.maximum_iterations = 50

        project.model = limit_state_example_1

        project.variables["a"].distribution = DistributionType.uniform
        project.variables["a"].minimum = -1
        project.variables["a"].maximum = 1

        project.variables["b"].distribution = DistributionType.uniform
        project.variables["b"].minimum = -1
        project.variables["b"].maximum = 1

        project.run()
        return project.design_point.reliability_index

    @staticmethod
    def openturns_beta() -> float:
        import openturns as ot
        from geoprob_pipe.calculations.system_calculations.example_parallel_system.limit_state_functions import (
            limit_state_example_1)

        a = ot.Uniform(-1.0, 1.0)
        b = ot.Uniform(-1.0, 1.0)

        marginal_distributions = [a, b]
        copula = ot.IndependentCopula(2)
        input_distribution = ot.ComposedDistribution(marginal_distributions, copula)

        def z1_function(xeta):
            return [limit_state_example_1(xeta[0], xeta[1])]

        python_function = ot.PythonFunction(2, 1, z1_function)

        input_random_vector = ot.RandomVector(input_distribution)
        output_random_vector_z = ot.CompositeRandomVector(python_function, input_random_vector)

        event_z = ot.ThresholdEvent(output_random_vector_z, ot.Less(), 0.0)
        event_z.setName('Z < 0.0')

        # Define optimization algorithm
        solver = ot.AbdoRackwitz()
        solver.setMaximumIterationNumber(10000)
        solver.setMaximumAbsoluteError(1.0e-3)
        solver.setMaximumRelativeError(1.0e-3)
        solver.setMaximumResidualError(1.0e-3)
        solver.setMaximumConstraintError(1.0e-3)
        solver.setStartingPoint(input_distribution.getMean())

        # Run the FORM algorithm
        event_form = ot.FORM(solver, event_z)
        event_form.run()
        result_z = event_form.getResult()
        result_z.setName('FORM Result for Z < 0.0')

        return result_z.getHasoferReliabilityIndex()


def test_dummy_reliability_calculation():
    expected_result = 2.77
    assert round(DummyReliabilityCalculation.prob_lib_beta(), 2) == expected_result
    assert round(DummyReliabilityCalculation.openturns_beta(), 2) == expected_result


class DummySystemReliabilityCalculation:

    @staticmethod
    def prob_lib_system_beta_combined_project():
        from probabilistic_library import (
            ReliabilityProject, ReliabilityMethod, DistributionType, CombineProject, CombinerMethod, CombineType)
        from geoprob_pipe.calculations.system_calculations.example_parallel_system.limit_state_functions import (
            limit_state_example_1, limit_state_example_2)

        project = ReliabilityProject()
        project.settings.reliability_method = ReliabilityMethod.form
        project.settings.variation_coefficient = 0.02
        project.settings.maximum_iterations = 50

        project.model = limit_state_example_1

        project.variables["a"].distribution = DistributionType.uniform
        project.variables["a"].minimum = -1
        project.variables["a"].maximum = 1

        project.variables["b"].distribution = DistributionType.uniform
        project.variables["b"].minimum = -1
        project.variables["b"].maximum = 1

        project.run()
        dp_z1 = project.design_point

        project.model = limit_state_example_2

        project.variables["c"].distribution = DistributionType.normal
        project.variables["c"].mean = 0.1
        project.variables["c"].deviation = 0.8

        project.run()
        dp_z2 = project.design_point

        print(f"reliability index Z1 = {dp_z1.reliability_index}")
        print(f"reliability index Z2 = {dp_z2.reliability_index}")

        combine_project = CombineProject()
        combine_project.design_points.append(dp_z1)
        combine_project.design_points.append(dp_z2)
        combine_project.settings.combiner_method = CombinerMethod.importance_sampling
        combine_project.settings.combine_type = CombineType.parallel
        combine_project.run()
        dp = combine_project.design_point
        print(f"reliability index S  = {dp.reliability_index}")

        max_limit_state_beta = max(dp_z1.reliability_index, dp_z2.reliability_index)
        diff_beta = abs(dp.reliability_index - max_limit_state_beta)
        diff_beta_perc = int((diff_beta / max_limit_state_beta) * 100)
        assert diff_beta_perc < 5, \
            (f"Voor een parallel systeem is het verschil tussen de maximale beta en de systeem beta klein. Maar in "
             f"dit geval is deze {diff_beta_perc}%.")
        # TODO Later Could Middel: De bovenstaande assertion triggert. Maar dat is fout.
        #  De gedachte was dat in een parallel systeem de maximale beta nagenoeg gelijk moet zijn de systeem beta. Ik
        #  test hier of de afwijking maximaal 5% is. Maar het hang er vanaf hoeveel invloed de gezamenlijke stochasten
        #  hebben, hoeveel de systeem beta afwijkt. Hoe dit precies zit weet ik nog niet. Maar is wellicht beter in te
        #  schatten als de invloedsfactoren worden geplot.

        return dp.reliability_index

    @staticmethod
    def prob_lib_system_beta_single_function():
        # from probabilistic_library import ReliabilityProject, ReliabilityMethod, DistributionType
        # from geoprob_pipe.calculations.system_calculations.example_parallel_system.limit_state_functions import (
        #     limit_state_example_1_and_2)
        #
        # project = ReliabilityProject()
        # project.settings.reliability_method = ReliabilityMethod.form
        # project.settings.variation_coefficient = 0.02
        # project.settings.maximum_iterations = 50
        #
        # project.model = limit_state_example_1_and_2
        #
        # project.variables["a"].distribution = DistributionType.uniform
        # project.variables["a"].minimum = -1
        # project.variables["a"].maximum = 1
        #
        # project.variables["b"].distribution = DistributionType.uniform
        # project.variables["b"].minimum = -1
        # project.variables["b"].maximum = 1
        #
        # project.variables["c"].distribution = DistributionType.normal
        # project.variables["c"].mean = 0.1
        # project.variables["c"].deviation = 0.8
        #
        # project.run()
        # return project.design_point.reliability_index
        pass  # TODO


def test_dummy_system_reliability_calculation():
    # expected_result = 3.12  # Aanname dat de prob lib beta van een combined project de juiste is.
    # assert round(DummySystemReliabilityCalculation.prob_lib_system_beta_combined_project(), 2) == expected_result
    # assert round(DummySystemReliabilityCalculation.prob_lib_system_beta_single_function(), 2) == expected_result
    # assert round(DummySystemReliabilityCalculation.openturns_system_beta(), 2) == expected_result
    # TODO Later Should Middel: Het zou goed zijn om voor dit simpele systeem ook betas te kunnen reproduceren.
    pass
