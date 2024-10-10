import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found
from classes.toolkit_native_model import ToolkitNative
from helper_functions.geodatabase_functions import process_geodatabase

from app.classes.fragility_curve import FragilityCurve

# toolkit_server_instance = ToolkitNative(
#     Path(r"C:\Program Files (x86)\Deltares\Probabilistic Toolkit\bin\Deltares.Probabilistic.Server.exe")
# )

# # Note: template tkx is only used to define probabilistic calculation settings, variable values are defined by this script using geodatabases
# path_template_tkx = r"C:\Users\MKL\OneDrive - Aveco De Bondt\Bureaublad\projecten_lokaal\WSHD detachering\Werkmap_PTK_Martijn\STPH\template.tkx"

# project = toolkit_server_instance.load(path_template_tkx)

# # Show name of STPH Python script that carries out all STPH calculations
# print(f"STPH script={project.model.script_file}")

# # Stuff with variables
# temp_list_var_means = [3, 2, 1]
# for index, var in enumerate(project.model.variables):
#     # Get variables that are required as arguments for the STPH py script
#     print(f"Variable {index}: {var.name}")

#     # Set values (these would be read from a geodatabase placed in the input folder by the user)
#     var.mean = temp_list_var_means[index]


# toolkit_server_instance.save(r"C:\Users\MKL\OneDrive - Aveco De Bondt\Bureaublad\projecten_lokaal\WSHD detachering\Werkmap_PTK_Martijn\STPH\template_modified.tkx")


FragilityCurve(
    r"C:\Users\MKL\OneDrive - Aveco De Bondt\Bureaublad\projecten_lokaal\WSHD detachering\Werkmap_PTK_Martijn\STPH\test_workspace",
    USE_EXISTING_TKX_RESULTS=False,
)

# path_gdb = r"C:\Users\MKL\OneDrive - Aveco De Bondt\Bureaublad\projecten_lokaal\WSHD detachering\Werkmap_PTK_Martijn\STPH\test.gdb"

# gdf = process_geodatabase(Path(path_gdb))
