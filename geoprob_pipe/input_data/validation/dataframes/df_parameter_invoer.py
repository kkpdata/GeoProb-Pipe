from typing import List
from geoprob_pipe.input_data.validation.dataframes.validation_objects import FailureQuery


FAILURE_QUERIES: List[FailureQuery] = [
    FailureQuery(
        query="distribution_type == 'cdf_curve' and fragility_values_ref.isnull()",
        msg="Geen referentie naar de fragility values gespecificeerd voor deze rij. Dit is vereist bij distributie "
            "type 'cdf_curve'."
    ),
    FailureQuery(
        query="distribution_type in ['normal', 'log_normal'] and mean.isnull()",
        msg="Geen gemiddelde waarde gespecificeerd voor deze rij. Dit is vereist bij distributie types 'normal' en "
            "'log_normal'."
    ),
    FailureQuery(
        query="distribution_type in ['normal', 'log_normal'] and variation.isnull() and deviation.isnull()",
        msg="Geen variatie coefficient of standaard deviatie gespecificeerd voor deze rij. Dit is vereist bij "
            "distributie types 'normal' en 'log_normal'."
    ),
    FailureQuery(
        query="parameter in ['d70', 'd70_m'] "
              "and distribution_type in ['deterministic', 'log_normal', 'normal'] "
              "and mean >= 0.001",
        msg="Parameter d70/d70_m moet een waarde hebben die kleiner is dan 0.001. Deze geef je op in de eenheid "
            "meters. Wellicht is de eenheid van de opgegeven waarde verkeerd?"
    ),
]
