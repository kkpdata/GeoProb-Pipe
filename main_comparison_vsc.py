from geoprob_pipe.comparisons.result_collect import ComparisonCollecter
from geoprob_pipe.comparisons.beta_dumbbell import dumbbell_uittredepunt

filepath1 = r"tests\systeem_testen\224\Traject224_model4a_WBN_prob.geoprob_pipe.gpkg"
filepath2 = r"tests\systeem_testen\224\Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg"
comparison = ComparisonCollecter(filepath1, filepath2)

dumbbell_uittredepunt(comparison)
