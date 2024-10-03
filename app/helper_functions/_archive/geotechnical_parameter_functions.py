from typing import Literal

from scipy.stats import t

MU = 24.6355
SIGMA = 8.626
n = 121
gamma = 1


def spatial_averaging(MU: float, SIGMA: float, n: int, gamma: float) -> tuple[float, float]:
    """Apply spatial averaging for D-Stability parameter distribution.

    Zie ook Handreiking Faalkansanalyse Macrostabiliteit (par. 5.1 en Tutorial C.1)

    Voor de invoer van kansverdelingen voor macrostabiliteit, dient ook
    rekening gehouden te worden met uitmiddeling bij lokale/regionale proevenverzamelingen,
    en statistische onzekerheid bij een steekproef met lage aantallen waarnemingen.

    Args:
        MU (float): mean
        SIGMA (float): standard deviation
        n (int): sample size
        gamma (float): variantiereductie factor, opties:  # FIXME checken gamma-waardes, uitleg hierbij in par. 5.1 lijkt af te wijken van uitleg in p. 107 in Handreiking
                       gamma^2 = 0 (lokale proeven verzameling)
                       gamma^2 = 0.25 (regionale proevenverzameling)
                       gamma^2 = 1.0 (puntwaardes, lokale proeven verzameling -> geen spatial averaging)

    Returns:
        MU_spatial_avg (float): spatially averaged mean
        SIGMA_spatial_avg (float): spatially averaged standard deviatoin
    """

    t95n = t.ppf(
        0.95, n - 1
    )  # t95,n de inverse cdf van de t-verdeling bij steekproefgrootte n is  #FIXME moet het 0.95 zijn of 0.05?
    z95 = 1.645  # z95 de inverse cdf van de normale verdeling, d.w.z. 1.645.  #FIXME het lijkt erop dat dit negatief moet zijn, zie p. 108 Handreiking
    transformatieverdeling = t95n / z95  # transformatiefactor tussen de twee verdelingen lognormal en student t

    MU_spatial_avg = MU
    SIGMA_spatial_avg = (
        SIGMA * transformatieverdeling * ((1 - gamma) ** 2 + (1 / n)) ** 0.5
    )  # FIXME lijkt een andere formule te zijn dan op p. 108 Handreiking

    return MU_spatial_avg, SIGMA_spatial_avg


MUdstab, SIGMAdstab = spatial_averaging(MU, SIGMA, n, gamma)
print(f"MUdstab: {MUdstab}")
print(f"SIGMAdstab: {SIGMAdstab}")
