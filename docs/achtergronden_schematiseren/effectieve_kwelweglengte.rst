Effectieve kwelweglengte
========================

Voor het mechanisme piping is de effectieve kwelweglengte een belangrijke sterkte parameter.
Afhankelijk van het gebruikte geohydrologische model wordt de kwelweglengte direct gedefinieerd of wordt deze afgeleid
uit overige parameters.

Zoals ook in :ref:`effectieve-voorlandlengte` is beschreven, maakt de kwelweglengte gebruik van het principe van de 
effectieve voorlandlengte door:

.. math::

   L_{kwelweg} = L_{but} + L_{eff,voorland}

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   \lambda_{1} = \sqrt{c_{voorland} \cdot k \cdot D_{wvp}}

waarin:

- :math:`L_{eff,voorland}` de effectieve voorlandlengte is [m]
- :math:`\lambda_{1}` de spreidingslengte van het voorland is [m]
- :math:`c` is de deklaagdikte gedeeld door de doorlatendheid van de deklaag [dag]

De effectieve kwelweglengte is altijd gemaximaliseerd op de lengte van het voorland :math:`L_{1}`. 
Daarom is het advies om de geografische ligging van de intredelijn :math:`L_{intrede}` zo te schematiseren dat de kweleglengte
fysisch gezien nooit groter kan zijn. Hierbij kan je ook rekening houden met eventuele radiale weerstand, 
bijvoorbeeld in het geval van een schaardijk.

De effectieve kwelweglengte van het voorland ligt altijd tussen de buitenteen en de intredelijn.


Omgang met verschillende scenario's
-----------------------------------


