"""
Collection of constants used thoughout the app
"""

# Default values and constants related to the input Excel file
ALLOWED_DISPERSION_TYPES = ["_stdev", "_vc"]  # Dispersion types (belonging to distribution types) that are allowed in the input Excel file. _stdev=standard deviation, _vc=variance coefficient
ALLOWED_SUFFIXES = ["_mean"] + ALLOWED_DISPERSION_TYPES  # Variable suffixes (not part of the variable name) allowed in the input Excel file (e.g. '_mean' in 'c_voorland_mean')
