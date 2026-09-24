Stap 2: Bepalen faalkans op vak- en trajectniveau
=================================================

De faalkans van een dijktraject wordt in GeoProb-Pipe opgebouwd vanuit individuele uittredepunten die samen een
seriesysteem vormen. Elk uittredepunt representeert een mogelijke locatie waar piping kan optreden, maar doordat deze
punten ruimtelijk dicht bij elkaar kunnen liggen is er sprake van onderlinge afhankelijkheid. 

Bij het assembleren van de uittredepunten tot een trajectkans zijn een aantal aannames gedaan, namelijk:

1. Doorsneden binnen een vak zijn statistisch homogeen. Een vak bestaat uit meerdere doorsneden waardoor de faalkans 
   van een vak groter is dan de faalkans van een enkele doorsnede.
2. De toename van de faalkans van een vak ten opzichte van een doorsnede wordt bepaald door een verschaling op 
   basis van equivalente onafhankelijke lengte :math:`(L_{vak}/\Delta L)`. 
3. Vakkansen zijn onafhankelijk verondersteld voor geotechnische faalmechanismen.

Voor een gegeven homogeen probleem is theoretisch het mogelijk om een zodanige equivalente onafhankelijke lengte te 
kiezen dat de benadering door deze assemblage exact overeenkomt met de werkelijke volledig probabilistische trajectkans.
Uit onderzoeken blijkt dat voor het mechanisme piping de equivalente onafhankelijke lengte :math:`\Delta L` tussen de 
100 en 300 m ligt. 

Binnen dit kader zijn in GeoProb-Pipe drie methoden geïmplementeerd om de trajectkans te benaderen, elk met een eigen
manier om met lengte-effect en afhankelijkheid tussen uittredepunten om te gaan: de WBI-methode, de Window-methode en
het opschalen van individuele secties. 

In GeoProb-Pipe is bij de initiële assemblage het uitgangspunt dat het hele vak pipinggevoelig is (``a=1``). Het is aan 
de gebruiker om aan de hand van de resultaten te controleren of dit uitgangspunt klopt. 

Om de gebruiker inzicht te geven in de mate van lengte-effect op dijktrajectniveau, worden bij de verschillende methoden
ook de ondergrens van de faalkans gepresenteerd. Hierbij ga je uit van een volledige afhankelijkheid tussen de uittredepunten. 


.. toctree::
   :maxdepth: 1

   stap2a_wbi_methode
   stap2b_window_methode
   stap2c_individuele_secties


