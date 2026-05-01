Van uittredepunt naar vak- en trajectkans
===========================================

De faalkans van een dijktraject wordt in GeoProb-Pipe opgebouwd vanuit individuele uittredepunten die samen een seriesysteem vormen. Elk uittredepunt representeert een mogelijke locatie waar piping kan optreden, maar doordat deze punten ruimtelijk dicht bij elkaar kunnen liggen is er sprake van onderlinge afhankelijkheid. Deze afhankelijkheid bepaalt in sterke mate de trajectkans, maar is in de praktijk niet exact bekend. Hierdoor kan de trajectfaalkans niet rechtstreeks worden bepaald door alle uittredepuntkansen simpelweg te combineren, maar moet deze worden benaderd binnen een bandbreedte die wordt begrensd door twee uitersten.

* **Bovengrens:** uitgaan van volledige onafhankelijkheid tussen uittredepunten, wat leidt tot een conservatieve inschatting (SOM-methode)
* **Ondergrens:** uitgaan van volledige afhankelijkheid tussen uittredepunten, wat leidt tot de minimale trajectfaalkans (MAX-methode)
* **Werkelijkheid:** de elementen in het seriesysteem hebben op voorhand een onbekende onderlinge afhankelijkheid. De mate van afhankelijkheid bepaalt de ‘werkelijke’ faalkans van het systeem. Echter, deze werkelijke faalkans is in de praktijk lastig te bepalen vanwege beperkingen in rekenkracht en geheugen, maar ook door beperkingen in beschikbare rekentechnieken. Daarom ligt de werkelijke situatie tussen de twee uitersten, maar kan deze niet exact worden vastgesteld.


Waarom niet gewoon probabilistisch combineren?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bij de uittredepuntenmethode worden in principe heel veel doorsneden doorgerekend. 
Als de dichtheid van uittredepunten groot genoeg is, is het voor het bepalen van de trajectkans voldoende om de uittredepunten te combineren op basis van hun onderlinge correlatie. 
Er is dus geen opschaling nodig onder de aanname van statistisch homogene vakken. Een voorwaarde is dat er geschikte probabilistische rekentechnieken toepasbaar zijn. 
De probabilistische rekentechnieken zijn beschikbaar maar beperkt toegankelijk en rekenintensief, waardoor dit nog niet is geïmplementeerd in GeoProb-Pipe.

In plaats daarvan zijn in eerdere projecten, zoals VNK-2 en de implementatie in Hydra-Ring, benaderingen ontwikkeld die uitgaan van statistisch homogene vakken. 
Binnen deze aanpak wordt de kans van een individuele doorsnede opgeschaald naar een vakkans via de outcrossing-methode, waarna vakkansen worden gecombineerd met de Hohenbichler-Rackwitz methode.
Deze aanpak vereist dat vakken voldoende groot zijn om beperkte onderlinge afhankelijkheid te garanderen, maar kan onnauwkeurigheden introduceren bij sterke correlaties tussen vakken. 
Daarom is het toepassen ervan afhankelijk van de beschikbaarheid van betrouwbare probabilistische input en goed gedefinieerde correlatiestructuren.
Waar Hydra-Ring uitgaat van expliciete probabilistische modellering van afhankelijkheid tussen doorsneden, 
benadert de WBI-methode dit effect indirect via een equivalente onafhankelijke lengte en een veronderstelde vakindeling.

Binnen dit kader zijn in GeoProb-Pipe drie methoden geïmplementeerd om de trajectkans te benaderen, 
elk met een eigen manier om met lengte-effect en afhankelijkheid tussen uittredepunten om te gaan: 
de WBI-methode, de windowmethode en het opschalen van individuele secties.