"""
Collection of constants that are used throughout the application.
"""

# #############
# Default values and constants related to the input Excel file
# #############

ALLOWED_DISPERSION_TYPES = ["_stdev", "_vc"]
# Dispersion types (belonging to distribution types) that are allowed in the input Excel file.
# _stdev=standard deviation, _vc=variance coefficient

ALLOWED_SUFFIXES = ["_mean"] + ALLOWED_DISPERSION_TYPES
# Variable suffixes (not part of the variable name) allowed in the input Excel file (e.g. '_mean' in 'c_voorland_mean')


DISTINCTIVE_COLORS = [
    '(60, 180, 75)', '(230, 25, 75)', '(255, 225, 25)', '(0, 130, 200)', '(245, 130, 48)', '(145, 30, 180)',
    '(70, 240, 240)', '(240, 50, 230)', '(210, 245, 60)', '(250, 190, 212)', '(0, 128, 128)',
    '(220, 190, 255)', '(170, 110, 40)', '(255, 250, 200)', '(128, 0, 0)', '(170, 255, 195)',
    '(128, 128, 0)', '(255, 215, 180)', '(128, 128, 128)', '(255, 255, 255)']
