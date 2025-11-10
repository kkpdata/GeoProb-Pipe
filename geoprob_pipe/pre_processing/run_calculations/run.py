from geoprob_pipe.pre_processing.parameter_input.expand_input_tables import run_expand_input_tables


def run_calculations(geopackage_filepath: str):
    df_expanded = run_expand_input_tables(geopackage_filepath=geopackage_filepath)
    df_expanded.to_excel("df_expanded.xlsx")
    raise NotImplementedError(f"Volgende stap nog te implementeren")
