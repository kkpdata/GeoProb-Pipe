

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
    def openturns_beta_v1():
        import openturns as ot

        a = ot.Uniform(-1.0, 1.0)
        b = ot.Uniform(-1.0, 1.0)
        c = ot.Normal(0.1, 0.8)

        marginal_distributions = [a, b, c]
        copula = ot.IndependentCopula(3)
        input_distribution = ot.ComposedDistribution(marginal_distributions, copula)

        def limitstate_function(xeta):
            alpha, beta, delta = xeta
            y1 = 1.9 - (alpha + beta)
            y2 = 1.85 - (1.5 * beta + 0.5 * delta)
            # parallel system: max of the two limit state functions
            y3 = max(y1, y2)

            return [y1, y2, y3]

        def z1_function(xeta):
            z1 = limitstate_function(xeta)
            return [z1[0]]

        f1 = ot.PythonFunction(3, 1, z1_function)

        input_random_vector = ot.RandomVector(input_distribution)
        output_random_vector_z1 = ot.CompositeRandomVector(f1, input_random_vector)

        event_z1 = ot.ThresholdEvent(output_random_vector_z1, ot.Less(), 0.0)
        event_z1.setName('Z1 < 0.0')

        solver = ot.AbdoRackwitz()
        solver.setMaximumIterationNumber(10000)
        solver.setMaximumAbsoluteError(1.0e-3)
        solver.setMaximumRelativeError(1.0e-3)
        solver.setMaximumResidualError(1.0e-3)
        solver.setMaximumConstraintError(1.0e-3)

        e1_form = ot.FORM(solver, event_z1, input_distribution.getMean())

        # run the FORM algorithm
        e1_form.run()

        result_z1 = e1_form.getResult()
        result_z1.setName('FORM Result for Z1 < 0.0')

        return result_z1.getHasoferReliabilityIndex()

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


# class Simple