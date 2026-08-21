.. _achtergronden-schematiseren-hierarchie:

Hiërarchie van invoerbronnen en detailniveaus
=============================================

GeoProb-Pipe combineert gegevens uit verschillende invoerbronnen om
scenarioberekeningen uit te voeren. Daarbij kunnen dezelfde parameters op
meerdere detailniveaus en vanuit verschillende bronnen beschikbaar zijn.

Deze pagina beschrijft:

* welke invoercategorieën door GeoProb-Pipe worden gebruikt;
* hoe invoerwaarden worden georganiseerd binnen trajecten, vakken en uittredepunten;
* hoe GeoProb-Pipe bepaalt welke waarde wordt gebruikt wanneer dezelfde parameter op meerdere niveaus of in meerdere bronnen aanwezig is.

Door deze hiërarchie toe te passen kan zowel met een globale als een
gedetailleerde schematisering worden gewerkt, waarbij de meest specifieke
beschikbare invoer altijd voorrang krijgt.

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

De invoercategorieën beschrijven welke gegevens beschikbaar zijn voor een
scenarioberekening. Binnen iedere invoercategorie kunnen parameters op
verschillende detailniveaus worden vastgelegd. Daarnaast kunnen parameterwaarden
afkomstig zijn uit verschillende invoerbronnen.

Voor het bepalen van de uiteindelijke invoerwaarde wordt daarom een vaste
hiërarchie toegepast op zowel detailniveau als invoerbron.

Detailniveaus
~~~~~~~~~~~~~

Parameterwaarden kunnen worden vastgelegd op de volgende detailniveaus:

* Traject
* Vak
* Uittredepunt

Hierbij geldt dat een meer specifiek detailniveau altijd voorrang heeft op een
meer algemeen detailniveau.

De prioriteitsvolgorde is daarom:

::

Uittredepunt > Vak > Traject

Wanneer voor een parameter een waarde beschikbaar is op meerdere detailniveaus, wordt altijd de meest specifieke waarde gebruikt.

Voorbeeld
^^^^^^^^^

Voor de parameter *top van de watervoerende zandlaag* zijn de volgende waarden
beschikbaar:

* Trajectniveau: -3 m + NAP
* Vakniveau: -2 m + NAP
* Uittredepuntniveau: niet ingevuld

In dit geval wordt de waarde op vakniveau gebruikt, omdat er geen waarde
beschikbaar is op uittredepuntniveau.

Wanneer ook op vakniveau geen waarde beschikbaar zou zijn, wordt de waarde op
trajectniveau gebruikt.

Invoerbronnen
~~~~~~~~~~~~~

Afhankelijk van de invoercategorie kunnen parameterwaarden afkomstig zijn uit
Excel of GIS.

Excel vormt hierbij de primaire bron voor parameterwaarden.
GIS levert aanvullende informatie, met name voor geometrische eigenschappen en
uittredepuntinformatie.

Binnen beide bronnen kan onderscheid worden gemaakt tussen:

* Algemene waarden
* Scenario-afhankelijke waarden

De beschikbare combinaties zijn:

::

    Uittredepunten
    ├─ Excel + Scenario's
    ├─ GIS + Scenario's
    ├─ Excel + Algemeen
    └─ GIS + Algemeen

    Vakken
    ├─ Excel + Scenario's
    └─ Excel + Algemeen

    Traject
    ├─ Excel + Algemeen
    └─ Scenario's (nader te bepalen)

Hierdoor wordt eerst bepaald op welk detailniveau een waarde beschikbaar is.
Vervolgens wordt binnen dat detailniveau de juiste bron en invoercategorie
gebruikt.
