from geoprob_pipe.cmd_app.comparisons import ComparisonCollector
import time

filepath1 = r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5.geoprob_pipe.gpkg"
filepath2 = r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5alt.geoprob_pipe.gpkg"
export_dir = r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe"

comparison = ComparisonCollector(filepath1,
                                 filepath2,
                                 export_dir)
start_time = time.time()
comparison.create_and_export_figures()
# comparison.dumbbell_beta().show()
# comparison.dumbbell_uplift().show()
# comparison.dumbbell_heave().show()
# comparison.dumbbell_piping().show()
# comparison.map_delta_beta_comparison().show()
# comparison.map_ratio_beta_comparison().show()
end_time = time.time()

print(f"Time passed for export: {end_time - start_time:.2f} sec")
