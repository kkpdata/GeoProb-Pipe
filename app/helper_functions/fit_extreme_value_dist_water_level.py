# -*- coding: utf-8 -*-
"""
Script for finding the extreme value (Gumbel) distribution parameters mu and sigma which is required as input for probabilistic macrostability calculations.
It is not integrated in the PTK macrostability tool; the user should use this as a standalone script and enter the resulting mu and sigma manually in the PTK macrostability tool.  

Note that this script is copied from the source below and is not optimized:
https://deltares.github.io/GEOLib-Plus/latest/community/probabilistic_macrostability/Tutorial_2_Fit_GEV_Distribution.html
"""
# %% import packages
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
from scipy.optimize import minimize
from scipy.stats import genextreme as gev
from scipy.stats import gumbel_r

# %% Load file
# Specify the directory where the JSON file is located
txt_directory = r"C:\Users\MKL\Downloads\Sourcetrail_2021_4_19_Windows_64bit_Installer"

# Specify the filename
txt_filename = "HydraNL_17-1_HM53.2_waterstandsverdeling_RP10.txt"

# Combine directory and filename to get the full path
txt_filepath = os.path.join(txt_directory, txt_filename)

# Open JSON file
with open(txt_filepath) as f:
    df = pd.read_csv(f, sep=",")  # Use Pandas to import the csv file. The headers are taken as column names
# %%Preprocessing of the data.
# Compute the freqency per yearand add it to the dataframe
df["FrequencyPerYear"] = 1 / df["ReturnPeriod"]
# Compute the exceedance probabilities from the frequency.
df["ExceedanceProbability"] = 1 - np.exp(-df["FrequencyPerYear"])
# Sort the water levels in ascending order
df.sort_values("WaterLevel", ascending=True)


# %%Visually checking the data
def plot_waterdata(ax):
    """
    Create a funtion to plot the waterdata, so we can later acess it again
    """
    ax.semilogy(df["WaterLevel"], df["ExceedanceProbability"], "bo", label="Data Points")
    ax.set_xlabel("Water Level h")
    ax.set_ylabel("Probability of exceedance")
    ax.grid(which="both")
    ax.legend()


plt.close("all")
ax = plt.subplot()
plot_waterdata(ax)
plt.show()

# %% Fitting a Generalized Extreme Value (GEV) distribution


def plot_GEV_cdf(ax, distribution_parameters):
    """
    Create a funtion to plot the cdf, so we can later acess it again
    """
    # Define a range of water levels for our fits
    # Base the bounds on the minimum and maximum of the data points.
    h_plotting_range = np.linspace(df["WaterLevel"].min() * 0.9, df["WaterLevel"].max() * 1.1, 100)

    # For each guess, we calculate the cdf values for the given range
    p_exc_fit = gev.cdf(
        h_plotting_range,
        c=distribution_parameters["shape"],
        loc=distribution_parameters["location"],
        scale=distribution_parameters["scale"],
    )

    # And plot the exceedance probability = 1 - cdf
    ax.semilogy(
        h_plotting_range,
        1 - p_exc_fit,
        label="Fitted GEV (shape={:.3g}, loc={:.3g}, scale={:.3g})".format(
            distribution_parameters["shape"], distribution_parameters["location"], distribution_parameters["scale"]
        ),
    )


# Re-instantiate the previous figure
ax = plt.subplot()
plot_waterdata(ax)

# We define different guesses for the shape, location, and scale parameter.
# Note we have a Frechet (shape<1,), Gumbel (shape=0), and Weibull (shape>1).
# Note that the opposite convention of the sign of the shape parameter in scipy, compared
# to several other sources (e.g. Wikipedia) and software packages (Probabilistic Toolkit).
distribution_parameters_list = [
    {"shape": -0.25, "location": 2.6, "scale": 0.01},  # Frechet
    {"shape": 0.00, "location": 2.5, "scale": 0.01},  # Gumbel
    {"shape": 0.25, "location": 2.6, "scale": 0.1},
]  # Weibull

# For each guess (distribution_parameter_set in distribution_parameter_set_list),
# calculate the cdf and plot it.
for distribution_parameters in distribution_parameters_list:
    plot_GEV_cdf(ax, distribution_parameters)

# Adjust the limits, and add labels
plt.ylim([1e-6, 1])
plt.title("Data and fitted GEV Distributions")
plt.legend()


# %% Optimizing the distribution parameters using Python
def square_log_err(
    params,
):
    """
    This function defines the sum of the squared log-differences
    between P_exc of the fitted GEV, and the P_exc of the data points.
    Note that we use gev.sf as the survival function (=1-cdf),
    and gev.logsf as the log of the survival function (=np.log(1-cdf)),
    because it is numerically more accurate with values close to 0.0/1.0.
    """
    shape, loc, scale = params
    data_h = df["WaterLevel"].iloc[:]
    data_p = df["ExceedanceProbability"].iloc[:]
    log_pexc_fit = gev.logsf(data_h, c=shape, loc=loc, scale=scale)
    log_err = log_pexc_fit - np.log(data_p)
    return np.sum(log_err**2)


# The minimization needs an initial guess for the parameters
# and bounds for the distribution parameters.
initial_guess = [0.00, 2.57, 0.1]
bounds = [(-1, 1), (0, 8), (0.01, 5)]

# Minimize squared difference to optimize the fit of the GEV distribution
result_gev = minimize(square_log_err, initial_guess, bounds=bounds)

# Extract the fitted parameters
fitted_shape, fitted_location, fitted_scale = result_gev.x
print("Fitted GEV: Shape, Location, Scale: {:.3g} {:.3g} {:.3g}".format(fitted_shape, fitted_location, fitted_scale))
print(
    "Note that for use in several other software packages (e.g. \n"
    "Probabilistic Toolkit), the opposite convention of the sign of \n"
    "the shape parameter c is used."
)

# %% Plot the result
# Re-instantiate the figure with water data
ax = plt.subplot()
plot_waterdata(ax)
distribution_parameters = {"shape": fitted_shape, "location": fitted_location, "scale": fitted_scale}
plot_GEV_cdf(ax, distribution_parameters)
plt.legend()
plt.show()

# %% Force fitting a Gumbel distribution
# For a Gumbel distribution, the shape parameter = 0, so adjust the bounds
initial_guess = [0.00, 2.1, 0.3]
bounds = [(0, 0), (1, 8), (0.01, 5)]


def square_log_err(
    params,
):
    """
    Define the logarithmic difference again.
    However, note that only the last 5 datapoints are used
    """
    shape, loc, scale = params
    data_h = df["WaterLevel"].iloc[-5:]
    data_p = df["ExceedanceProbability"].iloc[-5:]
    log_pexc_fit = gev.logsf(data_h, shape, loc=loc, scale=scale)
    log_err = log_pexc_fit - np.log(data_p)
    return np.sum(log_err**2)


# Make the fit
result_gumbel = minimize(square_log_err, initial_guess, bounds=bounds)
fitted_shape_gumbel, fitted_location_gumbel, fitted_scale_gumbel = result_gumbel.x
print(
    "Fitted Gumbel: Shape, Location, Scale: {:.3g} {:.3g} {:.3g}".format(
        fitted_shape_gumbel, fitted_location_gumbel, fitted_scale_gumbel
    )
)

# Re-instantiate the figure with water data
ax = plt.subplot()
plot_waterdata(ax)
distribution_parameters = {
    "shape": fitted_shape_gumbel,
    "location": fitted_location_gumbel,
    "scale": fitted_scale_gumbel,
}
plot_GEV_cdf(ax, distribution_parameters)
plt.legend()
plt.show()


print(
    "Note the opposite convention of the sign of the shape parameter c in scipy, compared to several other sources (e.g. Wikipedia) and software packages (Probabilistic Toolkit)."
)

print(
    f"\nInput for PTK probabilistic macrostability calculations:\nMU={fitted_location_gumbel}\nSIGMA DEV={fitted_scale_gumbel}"
)
print(
    f"\nIt is recommended to include the modus and 95th percentile (5% exceedance level) in the PTK calculations as fragility points. For the Gumbel distribution above, the corresponding waterlevels are:\nModus: NAP +{round(fitted_location_gumbel,2)} m (equal to MU for Gumbel)\n95th percentile: NAP +{round(gumbel_r.ppf(0.95, loc=fitted_location_gumbel, scale=fitted_scale_gumbel),2)} m"
)
