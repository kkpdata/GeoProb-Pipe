r""".. _stationair-model:

Model 4a: Stationair model
==========================

Op deze pagina volgt een uitleg van de implementatie van het stationaire model. Achtergronden staan in bijlage 4 van
het Technisch rapport Waterspanningen bij Dijken :cite:t:`trw_2004`.
Onder de aanname van horizontale stroming in het watervoerende zandpakket en verticale stroming in de weerstand
biedende deklaag is een analytische oplossing beschikbaar voor het debiet en het stijghoogteverloop in het zand.

.. figure:: /_static/model4a_trwd.png
   :width: 100%

   Schematisering grondwaterstroming stationair model (figuur b4.4 uit :cite:t:`trw_2004`)


Het stationaire model houdt in dat de respons op een gegeven locatie :math:`x` constant is. Op elke locatie is het
verband tussen de stijghoogte in het watervoerende pakket :math:`\phi(x)` en de respons :math:`r(x)` bekend door:

.. math::

    \phi(x) = h_{ref} + r(x) (h_{rivier} - h_{ref})

en andersom:

.. math::

    r(x) = \frac{(\phi(x) - h_{ref})}{(h_{rivier} - h_{ref})}

Aan het zandpakket met afdekkende kleilaag worden de volgende weerstanden gedefinieerd.
Voor het voorland:

.. math::

    W_{1} = \lambda_{1} tanh(\frac{L_{1}}{\lambda_{1}})

en voor het achterland:

.. math::

    W_{3} = \lambda_{3} tanh(\frac{L_{3}}{\lambda_{3}})

De totale weerstand is de som van bovenstaande weerstanden: :math:`\sum W = W_1 + L_2 + W_3`.

In het geval van een radiale (intrede)weerstand is er een extra weerstandsfactor gedefinieerd:

.. math::

    W_{radiaal} = 0.44 D

De radiale weerstand kan aan de totale weerstand :math:`\sum W` worden toegevoegd.

De respons ter plaatse van de buitenteen :math:`r_{but}` en de binnenteen :math:`r_{bit}` van de dijk is gedefinieerd als:

.. math::

    r_{but} = \frac{(W_2 + L_2)}{\sum W}

en

.. math::

    r_{bit} = \frac{(W_3)}{\sum W}

Het model neemt aan dat tussen de buitenteen en de binnenteen van de dijk er geen uitwisseling plaatsvindt tussen het
zandpakket en de deklaag. Over deze lengte :math:`L_2` wordt lineair geïnterpoleerd. Een bijzonder geval is
wanneer :math:`L_2 = 0`. We spreken dan van een kantelpunt. De definitie van de respons in het kantelpunt (zie
bladzijde b3-7 van :cite:`trw_2004)` is:

.. math::

    r_{kp} = \frac{1}{(1 + \frac{W_1}{W_3})}

Voor de faalmechanismen piping en macrostabiliteit is het potentiaalverloop verloop in de nabijheid van de dijk van
belang. Door de aanname van lineaire interpolatie wordt het potentiaalverloop beschreven door drie formules: één voor
het voorland tot de buitenteen, het gebied onder de dijk en een formulering voor het achterland. Hiervoor is het nodig
de :math:`x` positie in het dwarsprofiel te kennen. Deze module hanteert hiervoor de volgende definities:

De :math:`x` loopt op richting het achterland. De dijkzate is dan gedefinieerd als: :math:`L_2 = x_{bit} - x_{but}`.

Als :math:`x < x_{but}` dan ligt :math:`x` in het voorland en als :math:`x > x_{but}` dan ligt :math:`x` in het
achterland.

Voorland:

.. math::

    r(x) = 1.0 - (1.0 - r_{but}) \frac{sinh(\frac{L_{1} + x - x_{but}}{\lambda_{1}})}{sinh (\frac{L_{1}}{\lambda_{1}})}

    
Onder de dijk:

.. math::

    r(x) = r_{bit} + (r_{but} - r_{bit}) \frac{x_{bit} - x}{L_{2}}

Achterland: 

.. math::

    r(x) = r_{bit} \frac{sinh(\frac{L_{3} - x + x_{bit}}{\lambda_{3}})}{sinh (\frac{L_{3}}{\lambda_{3}})}

"""


import math
from dataclasses import dataclass
from typing import Tuple
from geoprob_pipe.calculations.physical_components.geohydro_functions import calc_lambda, calc_r_BIT, calc_r_BUT, calc_W


@dataclass
class Model4a:
    r"""Class for groundwater model 4A Technisch Rapport Waterspanningen bij Dijken
    """

    kD: float
    D: float
    c1: float
    c3: float
    L1: float
    L3: float
    x_but: float
    x_bit: float

    # noinspection PyPep8Naming
    @property
    def L2(self) -> float:
        return abs(self.x_bit - self.x_but)

    @property
    def lambda1(self) -> float:
        return calc_lambda(self.kD, self.c1)

    @property
    def lambda3(self) -> float:
        return calc_lambda(self.kD, self.c3)

    # noinspection PyPep8Naming
    @property
    def W1(self) -> float:
        return calc_W(self.lambda1, self.L1)

    # noinspection PyPep8Naming
    @property
    def W3(self) -> float:
        return calc_W(self.lambda3, self.L3)

    # noinspection PyPep8Naming
    @property
    def W_rad(self) -> float:
        return 0.44 * self.D

    # noinspection PyPep8Naming
    @property
    def W_tot4a(self) -> float:
        return self.W1 + self.L2 + self.W3

    # noinspection PyPep8Naming
    @property
    def r_BUT(self) -> float:
        return calc_r_BUT(self.W1, self.L2, self.W3)

    # noinspection PyPep8Naming
    @property
    def r_BIT(self) -> float:
        return calc_r_BIT(self.W1, self.L2, self.W3)

    def respons(self, x: float) -> Tuple[float, float, float]:
        """calculate response at x given model
        x positive direction is inwards, so x_but < x_bit"""

        # Before floodplain
        if x < self.x_but - self.L1:
            r = 1.0

        # Floodplain
        elif self.x_but > x >= self.x_but - self.L1:
            r = 1.0 - (1.0 - self.r_BUT) * math.sinh(
                (self.L1 + x - self.x_but) / self.lambda1
            ) / math.sinh(self.L1 / self.lambda1)

        # Hinterland (where potential is affected)
        elif self.x_bit < x <= self.x_bit + self.L3:
            r = (
                self.r_BIT
                * math.sinh((self.L3 - x + self.x_bit) / self.lambda3)
                / math.sinh(self.L3 / self.lambda3)
            )

        #
        elif x > self.x_bit + self.L3:
            r = 0.0

        # dike
        else:
            r = self.r_BIT + (self.r_BUT - self.r_BIT) * (self.x_bit - x) / (
                self.x_bit - self.x_but
            )

        return r, self.r_BUT, self.r_BIT