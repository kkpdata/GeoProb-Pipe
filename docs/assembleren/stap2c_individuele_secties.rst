Individuele secties-methode
===========================

Vaak zijn uittredepunten niet evenredig verdeeld over het dijktraject omdat geometrische kenmerken zoals maaiveldniveau
vooraf al een inschatting geven op welke punten piping een bijdrage kan hebben aan de trajectkans. 
Om inzicht te krijgen in de bovengrens van de trajectkans is een methode toegevoegd die automatisch individuele secties van een 
dijktraject identificeert en deze als onafhankelijke elementen combineert tot een trajectkans. 
Deze methode is gebaseerd op de veronderstelling dat uittredepunten binnen een korte afstand (5 m) van elkaar 
volledig afhankelijk zijn, terwijl uittredepunten die verder uit elkaar liggen als onafhankelijk worden beschouwd.

Het volgende algoritme is geïmplementeerd:

1.  Bepaal clusters van uittredepunten die in een window van 5 m in het dwarsprofiel liggen. Binnen een cluster met een
    window van 5 m is de veronderstelling van volledige afhankelijkheid en is de maximale faalkans van het cluster de
    doorsnedekans. Dit is het geselecteerde uittredepunt van het window.

2.  Bepaal de vaklengte op basis van de onderlinge afstand van de geselecteerde uittredepunten.

3.  Schaal de doorsnedekans op naar een vakkans uitgaande van :math:`a = 1` en :math:`\Delta L = 300 \, \mathrm{m}`.

4.  De onafhankelijke verzameling van uittredepunten bepaalt de trajectkans.