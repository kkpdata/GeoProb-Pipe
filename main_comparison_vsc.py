from geoprob_pipe.comparisons.comparison_collector import ComparisonCollecter
import geoprob_pipe.comparisons.beta_dumbbell as beta_dumbbell
from geoprob_pipe.comparisons.beta_map import map_beta_comparison

filepath1 = r"tests\systeem_testen\224\Traject224_model4a_WBN_prob.geoprob_pipe.gpkg"
filepath2 = r"tests\systeem_testen\224\Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg"
comparison = ComparisonCollecter(filepath1, filepath2)

beta_dumbbell.dumbbell_beta(comparison)
# beta_dumbbell.dumbbell_uplift(comparison)
# beta_dumbbell.dumbbell_heave(comparison)
# beta_dumbbell.dumbbell_piping(comparison)
map_beta_comparison(comparison)
