Het opschalen van individuele secties (Bovengrens van de trajectkans)
=====================================================================

De absolute bovengrens van de trajectkans is een onafhankelijke combinatie van alle uittredepunten in een dijktraject. 
Vaak zijn uittredepunten niet evenredig verdeeld over het dijktraject omdat geometrische kenmerken 
zoals maaiveldniveau vooraf al een inschatting geven op welke punten piping een bijdrage kan hebben aan de trajectkans.

Binnen een dwarsdoorsnede kunnen ook meerdere uittredepunten op korte afstand van elkaar gekozen zijn. 
Om een bovengrens van een trajectkans te bepalen is het volgende algoritme bedacht:

1.  Bepaal clusters van uittredepunten die in een window van 5 m in het dwarsprofiel liggen. 
    Binnen een cluster met een window van 5 m is de veronderstelling van volledige afhankelijkheid en is de maximale faalkans van het cluster de doorsnedekans. 
    Dit is het geselecteerde uittredepunt van het window.

2.  Bepaal de vaklengte op basis van de onderlinge afstand van de geselecteerde uittredepunten.

3.  Schaal de doorsnedekans op naar een vakkans uitgaande van :math:`a = 1` en :math:`\Delta L = 300 \, \mathrm{m}`.

4.  De onafhankelijke verzameling van uittredepunten bepaalt de trajectkans.