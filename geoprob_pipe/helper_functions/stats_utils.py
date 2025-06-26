import math
import scipy.stats as stats #importeer de scipy.stats module
import numpy as np

#lognormale verdeling
def calc_kar_waarde_met_Vc (Verwachtingswaarde: float, Vc: float, Percentiel: float, Shift = 0.0) -> float:
    r"""Berekening van de percentiel waarde van een lognormale verdeling 
    met variatiecoëfficiënt en verschuiving.

    Args:
        Verwachtingswaarde (float): verwachtingswaarde van de lognormale verdeling
        Vc (float): variatiecoëfficiënt van de lognormale verdeling
        Percentiel (float): percentiel waarvoor de waarde van de lognormale verdeling wordt berekend
        Shift (float, optional): verschuiving. Defaults to 0.0.

    Returns:
        float: percentiel waarde van de lognormale verdeling
    """
    sd = Vc * Verwachtingswaarde
    Vc_shift = sd / (Verwachtingswaarde - Shift)
    log_sd = math.sqrt(math.log(1.0 + math.pow(Vc_shift, 2.0)))
    log_mu = math.log(Verwachtingswaarde - Shift) - 0.5 * math.pow(log_sd, 2.0)
    return float(stats.lognorm.ppf(Percentiel, s = log_sd, loc = 0.0, scale = math.exp(log_mu))) + Shift


def calc_kar_waarde_met_sd(Verwachtingswaarde: float, sd: float, Percentiel: float, Shift = 0.0)-> float:
    r"""Berekening van de percentiel waarde van een lognormale verdeling 
    met standaarddeviatie en verschuiving.
    
    Args:
       Verwachtingswaarde (float): verwachtingswaarde van de lognormale verdeling
       sd (float): standaarddeviatie van de lognormale verdeling
       Percentiel (float): percentiel waarvoor de waarde van de lognormale verdeling wordt berekend
       Shift (float, optional): verschuiving. Defaults to 0.0.

    Returns:
       float: percentiel waarde van de lognormale verdeling
    """
    Vc_shift = float(sd / (Verwachtingswaarde - Shift))
    log_sd = math.sqrt(math.log(1.0 + math.pow(Vc_shift, 2.0)))
    log_mu = math.log(Verwachtingswaarde - Shift) - 0.5 * math.pow(log_sd, 2.0)
    return float(stats.lognorm.ppf(Percentiel, s = log_sd, loc = 0.0, scale = math.exp(log_mu))) + Shift

#normale verdeling
def calc_kar_waarde_normaal(Verwachtingswaarde: float, std: float, Percentiel: float) -> float:
    """Berekening van de percentiel waarde van een normale verdeling

    Args:
        Verwachtingswaarde (float): verwachtingswaarde van de normale verdeling
        std (float): standaarddeviatie van de normale verdeling
        Percentiel (float): percentiel waarvoor de waarde van de normale verdeling wordt berekend

    Returns:
        float: percentiel waarde van de normale verdeling
    """
    return float(stats.norm.ppf(Percentiel, loc= Verwachtingswaarde, scale=std))

#Berekenen parameters Gumbel verdeling

# a     = Gumbel location parameter
# b     = Gumbel dispersion parameter

#WBN = 15.12              # waterstand bij norm
#dec = 0.46               # decimeringshoogte 
#norm = 1/10000.0         # overschrijdingkans WBN

# Analytical solution a and b
#a = WBN + dec * np.log(-(np.log(1-norm))) / (np.log(-np.log(1-norm))-np.log(-np.log(1-norm/10)));
#b = dec /(np.log(-np.log(1-norm))-np.log(-np.log(1-norm/10)));

def calc_Gumbel_parameters(WBN: float, dec: float, norm: float, parameter = 'a') -> float:
    r"""Berekening van de parameters van de Gumbel verdeling op basis van WBN, decimeringshoogte 
    en overschrijdingskans van WBN

    Args:
        WBN (float): Waterstand Bij Norm in m+NAP
        dec (float): decimeringshoogte in m
        norm (float): overschrijdingskans WBN
        parameter (str, optional): a = Gumbel location(shift) parameter, 
        b = Gumbel dispersion(scale) parameter. Defaults to 'a'.

    Returns:
        float: parameter a of b van de Gumbel verdeling
    """
    if parameter == 'a':
        return WBN + dec * np.log(-(np.log(1-norm))) / (np.log(-np.log(1-norm))-np.log(-np.log(1-norm/10)))
    elif parameter == 'b':
        return dec /(np.log(-np.log(1-norm))-np.log(-np.log(1-norm/10)))
    else:
        return 999.0

#a = shift, b = scale

def calc_Gumbel_parameters_fromShiftScale(a: float, b: float, parameter = 'sd') -> float:
    """Berekening van de standaarddeviatie of de verwachtingswaarde van de Gumbel verdeling op 
    basis van de shift en scale parameters

    Args:
        a (float): Gumbel shift parameter
        b (float): Gumbel scale parameter
        parameter (str, optional): sd = standaarddeviatie of mean = gemiddelde. Defaults to 'sd'.

    Returns:
        float: _description_
    """    
    
    if parameter == 'sd': #standaardafwijking
        return (math.pi/math.sqrt(6.0)) * b
    elif parameter == 'mean': #mean 
        return a + (b * np.euler_gamma)
    else:
        return 999.0   

#todo: add tests
#todo: add type hints
#todo: van een karakteristieke waarde en een gemiddelde waarde de standaarddeviatie berekenen voor een lognormale verdeling


def calc_std_and_cv(percentile: float, mean: float, percentile_value: float) -> tuple:
    """
    Calculate the standard deviation and coefficient of variation for a normal distribution.

    Args:
        percentile (float): The percentile (e.g., 0.95 for the 95th percentile).
        mean (float): The mean of the normal distribution.
        percentile_value (float): The value at the given percentile.

    Returns:
        tuple: A tuple containing the standard deviation and the coefficient of variation.
    """
    # Calculate the z-score for the given percentile
    z = stats.norm.ppf(percentile)
    
    # Calculate the standard deviation
    std = (percentile_value - mean) / z
    
    # Calculate the coefficient of variation
    cv = std / mean
    
    return std, cv

# Example usage
#percentile = 0.95
#mean = 100
#percentile_value = 120
#std, cv = calc_std_and_cv(percentile, mean, percentile_value)
#print(f"Standard Deviation: {std}, Coefficient of Variation: {cv}")