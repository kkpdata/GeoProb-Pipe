Quick start
===========

`GeoProb-Pipe` neemt je mee door het gebruik van de applicatie. De quick start voor gebruik is daarom enkel de
installatie en het commando om de applicatie op te starten. Voer daarom de volgende twee commando's uit.

.. code-block:: bash

    pip install geoprob_pipe
    geoprob_pipe

In de onderstaande paragrafen is dieper in gegaan op het gebruik van `GeoProb-Pipe`.


Gebruik van GeoProb-Pipe
========================

Deze procesbeschrijving gaat uit van de uittredepuntenmethode in combinatie met het analytische stijghoogtemodel 4a. Het
gebruik bestaat uit de volgende stappen.

* Installatie

`GeoProb-Pipe` is in de basis een command line applicatie. Daardoor is de installatie simpel. Je start een nieuwe
virtuele Python omgeving en installeert de ``geoprob_pipe``-package. Zie paragraaf :ref:`installatie`.

* Pre-processing
Tijdens het pre-processen zet je de invoer voor de berekeningen klaar. Dit doe doe je door de `GeoProb-Pipe`-applicatie
op te starten. Deze neemt je vervolgens mee door alle stappen. In paragraaf :ref:`pre-processing` is hier verder op
ingegaan. Het resultaat van deze stap is een ``.geoprob_pipe.gpkp``-bestand. Dit bestand is een GeoPackage, te openen in
ArcGIS, met alle invoer.

* Berekeningen
Na het pre-processen vraagt `GeoProb-Pipe` of je de probabilistische berekeningen wilt uitvoeren. Deze keuze volgt na
het pre-processing menu. Deze stap bestaat enkel uit rekentijd. De ruwe data van de rekenresultaten worden toegevoegd
aan het ``.geoprob_pipe.gpkp``-bestand.

* Post-processing
Tijdens het post-processen worden alle resultaten geëxporteerd. Dit is inclusief ondersteunde bestanden zoals figuren.


.. _installatie:
Installatie en basis gebruik
----------------------------

Start een schone Python environment. `GeoProb-Pipe` is ontwikkelt op Python 3.12. Deze versie wordt aangeraden voor
gebruik. Voer daarna de volgende commando's uit om eerst `GeoProb-Pipe` te installeren en daarna de probabilistische
bibliotheek (PTK-tool wrapper) te installeren.


.. code-block:: bash

    pip install geoprob_pipe
    pip install probabilistic_library

Daarna start je de applicatie met het commando ``geoprob_pipe``. De applicatie zal je door het gebruik van de applicatie
leiden. Je kunt op elk moment de applicatie afsluiten, en weer opnieuw opstarten. Indien je geen `Afsluit`-knop/optie
ziet, dan kun je middels ``ctrl + c`` de applicatie stoppen.

In de volgende paragrafen is het gebruik van de applicatie verder toegelicht.


.. _pre-processing:
Pre Processing
----------------

Tijdens het pre-processen zet je de invoer voor de berekeningen klaar. De `GeoProb-Pipe` applicatie neemt je mee door
dit proces. Het bestaat uit de volgende stappen. Tijdens deze stappen wordt een ``.geoprob_pipe.gpkp``-bestand
aangemaakt. Dit is een GeoPackage waarin alle invoer, en later eveneens rekenresultaten, worden opgeslagen.

Algemene instellingen / Model keuze
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Er zijn enkele algemene instellingen, dit is hoofdzakelijk de systeem keuze. Momenteel is enkel `Piping`` een keuze.
Later wordt dit uitgewerkt naar onder andere de keuzes ``model4a`` en deze i.c.m. Moria en/of het toepassen van
respons.


Importeren GIS-data
~~~~~~~~~~~~~~~~~~~

`GeoProb-Pipe` vraagt je stapsgewijs om de GIS-data te importeren. Hij zal je vragen naar de locatie van de data. Dit
kun je aanleveren als Shape-bestand, GeoDatabase of GeoPackage. De GIS data is bijvoorbeeld het dijktraject, de
vakindeling en de uittredepunten. Omdat je de applicatie op elk moment kunt afsluiten, kun je ook eerst een deel van de
GIS-data importeren en later verder gaan. Bijvoorbeeld, voor de uittredepunten locaties kan `GeoProb-Pipe` voor jou een
eerste suggestie maken, waarna jij deze in ArcGIS zelf verder kunt aanvullen.

Omdat `GeoProp-Pipe` een GeoPackage is, kan je alle geïmporteerde data in ArcGIS bekijken en controleren of het goed is
geïmporteerd.

Aan het einde van het importeren van alle GIS-data zal `GeoProb-Pipe` vinkjes geven voor elk onderdeel. Dit ziet er
als het volgt uit.

.. code-block:: bash

    GIS LAGEN
     ✔  Dijktraject al toegevoegd.
     ✔  Vakindeling al toegevoegd.
     ✔  HRD-bestanden al toegevoegd.
     ✔  HRD-locatie punten al uitgelezen.
     ✔  Uittredepunten al toegevoegd (58 in totaal).
     ✔  Polderpeil al toegevoegd.
     ✔  Binnenteenlijn al toegevoegd.
     ✔  Buitenteenlijn al toegevoegd.
     ✔  Intredelijn al toegevoegd.

    GEOGRAFISCHE KOPPELINGEN
     ✔  HRD-locaties al gekoppeld aan uittredepunten.
     ✔  Afstanden intrede, buitenteen en binnenteen al gekoppeld aan uittredepunten.
     ✔  Polderpeil al gekoppeld aan uittredepunten.
     ✔  Afstand en metrering tot reflijn al gekoppeld aan uittredepunten.
     ✔  Vakken al gekoppeld aan uittredepunten.



Importeren parameter invoer
~~~~~~~~~~~~~~~~~~~~~~~~~~~




Dit doe doe je door de `GeoProb-Pipe`-applicatie
op te starten. Deze neemt je vervolgens mee door alle stappen. In paragraaf :ref:`pre-processing` is hier verder op
ingegaan. Het resultaat van dit bestand is een .geoprob_pipe.gpkp-bestand. Dit bestand is een GeoPackage, te openen in
ArcGIS, met alle invoer.



Vastleggen algemene uitgangspunten van de berekening
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vastleggen uittredepunten
~~~~~~~~~~~~~~~~~~~~~~~~~

De volgende informatie dient te worden vastgelegd per uittredepunt:

* `UittredepuntID`: elk punt heeft een eigen identifer
* `Locatie (x, y)`: locatie in RD coördinaten (bijv. geopandas-object)
* `Mvalue`: waarde die de locatie van het uittredepunt weergeeft ten opzichte van de referentielijn. zie voorbeelden over linear referencing.
* `Uittredelocatie`: optioneel, beschrijving van de locatie van het uittredepunt. Handig voor analyse van de berekeningen.
* (Ruimtelijke) koppeling met het vak van de ondergrondschenario: `VakID` en `Vaknaam`. 
* `DIST_L_GEOM`: kortste afstand tot de geschematiseerde `geometrische intredelijn`.
* `DIST_BUT`: korste afstand tot de geschematiseerde `buitenteen lijn`.
* `DIST_BIT`: korste afstand tot de geschematiseerde `binnenteen lijn`.
* `HydraLocatie`: ruimtelijke koppeling met de dichtsbijzijnde uitvoerlocatie. 
* `Bodemhoogte`: bodemhoogte (maaiveldniveau) ter plaatse van het uittredepunt.
* `Polderpeil`: benedenstroomse waterpeil ter plaatse van het uittredepunt.

De werkwijze is als volgt:

1. definieer uittredepunten in GIS omgeving: dit levert `UittredepuntID`, `Locatie (x, y)`
2. Bepaal `Mvalue` via linear referencing aan de `referentielijn`.
3. Koppel `uittredepunten` aan `vakindeling`: dit levert `VakID` en `Vaknaam`.
4. Bepaal `DIST_L_GEOM`, `DIST_BUT`, `DIST_BIT` door spatial join met `Geometrische Intredelijn`, `Buitenteen` en `Binnenteen`.
5. Bepaal `Bodemhoogte` door samplen raster met DTM/AHN
6. Bepaal `Polderpeil` door intersectie met een polygon `Polderpeilen`.
7. Koppel `HydraLocatie` aan `Overschrijdingsfrequenties`.


Discussie uittredepunten tabel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. De geometrische lengte van het achterland `L3_geom` is nu vastgelegd per vak. Dit is een parameter die niet heel precies vastgelegd hoeft te worden en vaak vooraf onbekend is. In lijn met `DIST_BUT` kan `L3_geom` ook worden vastgelegd als een geometrie en als veld aan het object `uittredepunten` worden toegevoegd.

2. Optioneel kan het model worden uitgebreid met de verwachte top van het zand ter plaatse van het uittredepunt.


### Bronbestanden voor de uittredepunten tabel

De locaties van mogelijke uittredepunten

Uitvoer van een Hydra-NL berekening
TODO: format vastleggen

### Vastleggen Ondergrondschematisatie

### Genereren scenarioberekeningen

## Uitvoeren scenarioberekeningen

### Semi-probabilistische berekeningen

### Probabilistische berekeningen

## Verwerken scenarioberekeningen