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

De effectieve kwelweglengte van het voorland ligt altijd tussen de buitenteen en de intredelijn en is 
altijd gemaximaliseerd op de lengte van het voorland :math:`L_{1}`. 
Daarom is het advies om de geografische ligging van de intredelijn :math:`L_{intrede}` zo te schematiseren dat de kweleglengte
fysisch gezien nooit groter kan zijn. Hierbij kan je ook rekening houden met eventuele radiale weerstand, 
bijvoorbeeld in het geval van een schaardijk.

De weerstand van het voorland (en de daaruit volgende spreidingslengte) is een onzekere variabele die de weerstand over 
een groot oppervlak van het voorland beschrijft. Zonder metingen is de kennisonzekerheid groot en vindt de schematisatie
plaats op basis van ervaring en gebiedskennis. 

Bij het gebruik van model 4a is het vaak niet nodig om apart voor de weerstand in het voorland meerdere scenario's te definiëren.
De spreidingslengte wordt namelijk afgeleid uit de weerstand van de deklaag en de eigenschappen van het watervoerend pakket.
Het gaat erom om dat de combinatie van variabelen past bij fysieke kenmerken van het voorland. 


Omgang met verschillende scenario's
-----------------------------------

.. figure:: /_static/EffectieveVoorlandlengte_enkel.png
   :width: 100%

   Effectieve voorlandlengte bij een enkel scenario



.. figure:: /_static/EffectieveVoorlandlengte_dubbel.png
   :width: 100%

   Effectieve voorlandlengte bij een dubbel scenario. De effectieve voorlandlengte wordt bepaald door de mate van 
   weerstand in het voorland die per scenario kan worden opgegeven.
