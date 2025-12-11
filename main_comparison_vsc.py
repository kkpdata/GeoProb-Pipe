from geoprob_pipe.comparisons import ComparisonCollecter
import time

filepath1 = r"tests\systeem_testen\224\Traject224_model4a_WBN_prob.geoprob_pipe.gpkg"
filepath2 = r"tests\systeem_testen\224\Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg"
export_dir = r"tests\systeem_testen\224"

comparison = ComparisonCollecter(filepath1,
                                 filepath2,
                                 export_dir)
start_time = time.time()
comparison.dumbell_beta().show()
comparison.dumbell_uplift().show()
comparison.dumbell_heave().show()
comparison.dumbell_piping().show()
comparison.map_delta_beta_comparison().show()
comparison.map_ratio_beta_comparison().show()
end_time = time.time()

print(f"Time passed for export: {end_time - start_time:.2f} sec")
