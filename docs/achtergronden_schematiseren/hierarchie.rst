Hierarchie van de invoer
========================
GeoProb-Pipe combineert informatie uit verschillende databronnen om een scenarioberekening uit te voeren. 
Voor iedere berekening wordt een unieke combinatie van geometrie, uittredepuntgegevens en ondergrondparameters samengesteld.

Invoercategorieën
-----------------
De schematisering bestaat uit drie categorieën invoer:

Geometrische eigenschappen
~~~~~~~~~~~~~~~~~~~~~~~~~~

Deze gegevens worden via GIS-bestanden aangeleverd en beschrijven de ligging van het traject en de ruimtelijke kenmerken van de kering. Deze kunnen later via de excel of de geopackage (in de toekomst) worden aangepast. Hieronder vallen onder andere:

-   trajectlijn;
-   vakindeling;
-   HRD-locaties;
-   buitenteenlijn;
-   binnenteenlijn;
-   intredelijn;
-   polderpeilen.

Uittredepunten
~~~~~~~~~~~~~~
Uittredepunten worden aangeleverd als puntenbestand. Een uittredepunt beschrijft de locatie waarop een pipingberekening wordt uitgevoerd. Naast de locatie bevat een uittredepunt bijvoorbeeld informatie over:
-   maaiveldhoogte ter plaatse van het uittredepunt.
-   wordt gecombineerd met de geometrische gegevens om afstand tot de buitenteenlijn en binnenteenlijn te bepalen.

Ondergrondscenario's
~~~~~~~~~~~~~~~~~~~~
Ondergrondscenario's worden aangeleverd via een Excelbestand. Hierin worden onder andere de ondergrondeigenschappen vastgelegd, zoals:

-   top van de watervoerende zandlaag;
-   dikte van de zandlaag;
-   doorlatendheid (k-waarde);
-   weerstand van het voorland (c-waarde).

Deze drie categorieën vormen gezamenlijk de invoer voor een scenarioberekening. Elke scenarioberekening wordt uitgevoerd voor een specifieke combinatie van geometrie, uittredepunt en ondergrondscenario.

Prioriteit van invoerwaarden
----------------------------

Voor veel invoerparameters kunnen waarden op verschillende niveaus worden opgegeven. Hierdoor kan zowel met een grove als een gedetailleerde schematisering worden gewerkt.

Wanneer een parameter op meerdere niveaus beschikbaar is, wordt de meest specifieke waarde gebruikt. De prioriteitsvolgorde is:
uittredepuntniveau > vakniveau > trajectniveau.

Dit betekent dat GeoProb-Pipe eerst controleert of een parameter voor het betreffende uittredepunt is opgegeven. Wanneer geen waarde beschikbaar is, wordt gekeken naar een waarde op vakniveau. 
Indien ook daar geen waarde aanwezig is, wordt de waarde op trajectniveau gebruikt. Voor zowel geometrische eigenschappen als ondergrondscenario's geldt dezelfde systematiek.

Voorbeeld
~~~~~~~~~ 
Top van de watervoerende zandlaag zijn de volgende waarden beschikbaar:
-   Trajectniveau: -3 m + NAP
-   Vakniveau: -2 m + NAP
-   Uittredepuntniveau: niet ingevuld
In dit geval wordt de waarde op vakniveau gebruikt, omdat er geen waarde beschikbaar is op uittredepuntniveau. Wanneer ook op vakniveau geen waarde beschikbaar zou zijn, wordt de waarde op trajectniveau gebruikt.



