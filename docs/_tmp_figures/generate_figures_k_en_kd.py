from probabilistic_library import Stochast, DistributionType
import numpy as np
import matplotlib.pyplot as plt

def plot_dist(val_grid, stochast, title):

    pdf = [stochast.get_pdf(val) for val in val_grid]
    cdf = [stochast.get_cdf(val) for val in val_grid]
    
    fig, ax1 = plt.subplots()
    color = "tab:blue"
    ax1.set_xlabel("value (-)")
    ax1.set_ylabel("pdf (-)", color=color)
    ax1.plot(val_grid, pdf)
    ax1.tick_params(axis="y", labelcolor=color)
    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("cdf (-)", color=color)
    ax2.plot(val_grid, cdf, "r--", label="pdf")
    ax2.tick_params(axis="y", labelcolor=color)
    fig.suptitle(title)

def plot_k():
    pass

def plot_kd():
    pass

def model_kD_from_k_and_D(k: float, D: float) -> float:
    """
    Model the kD from k and D
    :param k: rate constant
    :param D: diffusion coefficient
    :return: kD
    """
    return k * D

def model_k_from_kD_and_D(kD: float, D: float) -> float:
    """
    Model the k from kD and D
    :param kD: rate constant
    :param D: diffusion coefficient
    :return: k
    """
    return kD / D

# define stochastic variables
# kD
kD = Stochast()
kD.distribution = DistributionType.log_normal
kD.location= 3000.0
kD.scale = 0.4*kD.location

# k
k = Stochast()
k.distribution = DistributionType.log_normal
k.location = 55.0
k.scale = 0.5*k.location

# D
D = Stochast()
D.distribution = DistributionType.log_normal
D.location = kD.location / k.location
D.scale = 1.5

def main():
    pass    

if __name__ == "__main__":
    main()
