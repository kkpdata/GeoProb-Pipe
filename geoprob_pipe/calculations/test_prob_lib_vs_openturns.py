

class DummyReliabilityCalculation:

    @staticmethod
    def prob_lib_beta():
        from probabilistic_library import ReliabilityProject, ReliabilityMethod, DistributionType
        from geoprob_pipe.calculations.limit_state_functions import limit_state_example_1

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
    def openturns_beta():
        import openturns as ot
        from geoprob_pipe.calculations.limit_state_functions import limit_state_example_1

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


# class DummySystemReliabilityCalculation:

