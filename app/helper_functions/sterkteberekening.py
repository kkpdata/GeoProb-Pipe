import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

from deklaag import dikte_effectieve_deklaag
from kwelweglengte import kwelweglengte_func

# Vaste parameters STPH (!!!waarschijnlijk!!! onafhankelijk van traject, komt dit in PTK tool zelf?)
gamma_w = 9.81  # [kN/m3]   Soortelijk gewicht water
i_toelaatbaar = 0  # [-]	    (Verticale) uittredeverhang
theta = 37.0  # [°]	    Rolweerstandshoek van de zandkorrels
nu = 1.33e-06  # [m2/s]	Kinematische viscositeit (voor grondwater van 10° Celsius)
g = 9.81  # [m/s2]	Valversnelling
eta = 0.25  # [-]	    Coëfficiënt van White (Sleepfactor)
gamma_p = 16.19  # [kN/m3]	(Schijnbaar) volumegewicht van de zandkorrels onder water
d_70m = 2.08e-04  # [m]	    Gemiddelde d70 in de kleine schaalproeven
rc = 0.3  # [-]	    Reductiefactor weerstand bij uittredepunt

# Faalkanseis en norm (trajectafhankelijk dus mogelijk GEOdatabase?)
a_traject = 0.4  # [-]
b_traject = 300  # [m]
Signaleringswaarde = 1.00e-03  # [1/jaar]
Ondergrens = 3.33e-03  # [1/jaar]
L_traject = 19779.82  # [m]
betanorm = 3.1  # [1/year]	Betrouwbaarheidsindex van het dijktraject
norm = 1000  # [1/year]	Signaleringswaarde van het traject

N_traject = 1 + a_traject * L_traject / b_traject  # [-]
w_traject = 0.24  # [-]
Peis_sig_dsn = Signaleringswaarde * w_traject / N_traject  # 1/jaar
Peis_ond_dsn = Ondergrens * w_traject / N_traject  # 1/jaar
Peis_ond = Ondergrens  # 1/jaar
