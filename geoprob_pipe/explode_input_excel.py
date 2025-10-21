from pandas import DataFrame, read_excel

path_to_excel = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\geoprob_pipe\pre_processing\parameter_input\input_voorstel_v3.xlsx"


df: DataFrame = read_excel(path_to_excel, sheet_name="Parameter invoer", header=3)

