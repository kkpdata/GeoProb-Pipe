

def test_collector():
    ##

    from geoprob_pipe.cmd_app.comparisons import ComparisonCollector
    import os
    import shutil
    from repo_utils.utils import repository_root_path

    export_dir = os.path.join(os.getcwd(), "tmp_exports", "comparison_collector")
    os.makedirs(export_dir, exist_ok=True)
    repo_root = repository_root_path()
    filepath1 = os.path.join(repo_root, "tests", "systeem_testen", "224", "unit_testset_dt224.geoprob_pipe.gpkg")
    filepath2 = os.path.join(
        repo_root, "tests", "systeem_testen", "224", "unit_testset_dt224_for_comparison.geoprob_pipe.gpkg")
    obj = ComparisonCollector(geopackage_filepath_1=filepath1, geopackage_filepath_2=filepath2, export_dir=export_dir)
    obj.create_and_export_figures()
    shutil.rmtree(export_dir)

    ##
