Invoergegevens importeren
=========================

Tijdens het importeren van de invoergegevens doorloop je de onderstaande stappen. Wanneer alle stappen een
vinkje hebben, zijn alle gegevens volledig ingevoerd.


.. code-block:: bash

    ALGEMEEN
     ✔  Geohydrologisch model al ingesteld.

    GIS LAGEN
     ✔  Dijktraject al toegevoegd.
     ✔  Vakindeling al toegevoegd.
     ✔  HRD-bestanden al toegevoegd.
     ✔  HRD-locatie punten al uitgelezen.
     ✔  HRD-fragility lines al uitgelezen.
     ✔  Uittredepunten al toegevoegd (#### in totaal).
     ✔  Polderpeil al toegevoegd.
     ✔  Binnenteenlijn al toegevoegd.
     ✔  Buitenteenlijn al toegevoegd.
     ✔  Intredelijn al toegevoegd.

    GEOGRAFISCHE KOPPELINGEN
     ✔  Afstand en metrering tot reflijn al gekoppeld aan uittredepunten.
     ✔  HRD-locaties al gekoppeld aan uittredepunten.
     ✔  Afstanden intrede, buitenteen en binnenteen al gekoppeld aan uittredepunten.
     ✔  Polderpeil al gekoppeld aan uittredepunten.
     ✔  Vakken al gekoppeld aan uittredepunten.

    PARAMETER INVOER
     ✔  Parameter invoer afgerond.



Algemeen
^^^^^^^^
Er is één algemeen item in het invoerproces, namelijk de keuze van het geohydrologische model. Dit is een vertaling van
de grondwaterstroming als gevolg van het hoogwater, met als resultaat van het model een schatting van de stijghoogte in
het uittredepunt. Momenteel zijn 3 modellen ingebouwd, waaronder het veel gebruikte model 4A. Een gedetailleerde
beschrijving vind je :ref:`hier<stijghoogtemodellen-geoprob>`.


GIS lagen & Geografische koppelingen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In het onderdeel 'GIS lagen' wordt de gebruiker gevraagd om verschillende geografische datasets te importeren. Dit
betreft onder andere het dijktraject, de vakindeling, de uittredepunten en de intredelijn. Gegevens kunnen worden
ingelezen vanuit een Shapefile, GeoDatabase of GeoPackage.

Na het importeren van de geografische data worden de benodigde geografische koppelingen automatisch gelegd. Hierbij
worden de verschillende datasets voornamelijk gekoppeld aan de uittredepunten, zoals het polderpeil.


Parameter invoer
^^^^^^^^^^^^^^^^


.. TODO: Waar beschrijven we hoe parameter invoer elkaar kan overlappen?






Na het inladen van de geografische data wordt dit automatisch gekoppeld aan de uittredepunten en vakken.

Tot slot verzoekt de applicatie je om de resterende invoer te definiëren in een Excel template.


.. TODO: Verwijzingen aanmaken.



Rekenmodel
~~~~~~~~~~

Er zijn enkele algemene instellingen, dit is hoofdzakelijk de systeem keuze. Momenteel is enkel `Piping`` een keuze.
Later wordt dit uitgewerkt naar onder andere de keuzes ``model4a`` en deze i.c.m. Moria en/of het toepassen van
respons.
:ref:`Rekenmethodiek <rekenmethodiek>`

Verschalingsfactoren
~~~~~~~~~~~~~~~~~~~~

sdfsdf


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


Typen ondergrondscenario's
~~~~~~~~~~~~~~~~~~~~~~~~~~

Een ondergrondscenario is een unieke verzameling van variabelen die de eigenschappen van de ondergrond beschrijven. Ondergrondscenario's  worden per vak of per uittredepunt vastgelegd. Er zijn drie typen ondergrondscenario's:

- Holoceen gefundeerd (HLF): Hierbij zit de deklaag boven een holocene zandlaag welke samen met de onderliggende pleistocene zandlaag het watervoerend pakket vormen.
- Pleistoceen (PL): Hierbij ligt de deklaag direct boven op een pleistocene zandlaag.
- Tussenzandlaag: Hierbij is er nog een tussenzandlaag aanwezig omsloten door de deklaag en een andere kleilaag. Deze is niet in direct contact met het pleistocene watervoerend pakket.

Een kenmerk van ondergronscenario's is dat ze discreet zijn. Of het ene scenario komt voor binnen een vak of het andere. Afhankelijk van de beschikbare data kan je per uittredepunt de ondergrondscenario's vastleggen. We kiezen er in deze implementatie voor om per vak een ondergrondscenario vast te leggen. Dit betekent dat alle uittredepunten binnen een vak dezelfde (typen) ondergrondscenario's hebben.

.. figure:: /_static/TypenOndergrondscenario.png
   :width: 100%

   Voorbeeld typen ondergrondscenario's


.. TODO:

    Bronbestanden voor de uittredepunten tabel
    De locaties van mogelijke uittredepunten
    Uitvoer van een Hydra-NL berekening
    Vakindeling
    Genereren scenarioberekeningen
    Uitvoeren scenarioberekeningen
    Probabilistische berekeningen
    Combineren deelfaalmechanismen
    Combineren scenarioberekeningen
    Post Processing
