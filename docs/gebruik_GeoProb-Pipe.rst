Quick start
===========

`GeoProb-Pipe` neemt je mee door het gebruik van de applicatie. De quick start voor gebruik is daarom enkel de
installatie en het commando om de applicatie op te starten. Dat zijn de volgende twee commando's.

.. code-block:: bash

    pip install geoprob_pipe
    geoprob_pipe

In de onderstaande paragrafen is dieper in gegaan op het gebruik van `GeoProb-Pipe`.


Gebruik van GeoProb-Pipe
========================

GeoProb-Pipe is een command line-applicatie met een eenvoudig **installatieproces**. Je begint met het aanmaken van een
nieuwe virtuele Python-omgeving en installeert vervolgens de ``geoprob_pipe``-package. Zie de paragraaf
:ref:`installatie` voor meer details.

Tijdens het **pre-processen** bereid je de invoerdata voor. De applicatie begeleidt je stap voor stap door het proces.
In de paragraaf :ref:`pre-processing` wordt dit verder toegelicht. Het resultaat van deze stap is een
``.geoprob_pipe.gpkp``-bestand waarin alle invoer geografisch is gerefereerd en geschikt is voor gebruik als GeoPackage
in ArcGIS of QGIS.

Na het pre-processen vraagt GeoProb-Pipe of je de **probabilistische berekeningen** wilt uitvoeren. Deze stap bestaat
uitsluitend uit rekentijd. De resultaten van de berekeningen worden toegevoegd aan het ``.geoprob_pipe.gpkp``-bestand.

Tijdens het **post-processen** worden alle resultaten geëxporteerd, waaronder ruwe data en visualisaties.


.. _installatie:
Installatie en basis gebruik
----------------------------

De installatie en het gebruik van `GeoProb-Pipe` is eenvoudig en wordt hieronder toegelicht.

Start een schone Python environment. `GeoProb-Pipe` is ontwikkelt op Python 3.12. Deze versie wordt aangeraden voor
gebruik. Voer daarna de volgende commando's uit om eerst `GeoProb-Pipe` te installeren en vervolgens de probabilistische
bibliotheek (PTK-tool wrapper) te installeren.


.. code-block:: bash

    pip install geoprob_pipe
    pip install probabilistic_library

.. TODO: Overleggen met Deltares dat ze de probabilistic_library beschikbaar maken in PyPI.

Daarna start je de applicatie met het commando. Zorg er voor dat je Python-environment actief is.

.. code-block:: bash

    geoprob_pipe

Na het opstarten van de applicatie begeleidt `GeoProb-Pipe` je door het gebruik. Je kunt op elk moment de applicatie
afsluiten, en weer opstarten. Meestal geeft de applicatie je de mogelijkheid om af te sluiten, is dit niet het geval,
dan kun je dat doen middels de toetsencombinatie ``ctrl + c``.


.. _pre-processing:
Pre-processing
--------------

Tijdens het pre-processen zet je de invoer klaar. `GeoProb-Pipe` neemt je mee door dit proces. Aan het einde zul je
een vinkje hebben voor elk onderdeel.

.. code-block:: bash

    ALGEMEEN
     ✔  Belastingmodel al ingesteld.
     ✔  Verschalingsfactoren al ingesteld.

    GIS LAGEN
     ✔  Dijktraject al toegevoegd.
     ✔  Vakindeling al toegevoegd.
     ✔  HRD-bestanden al toegevoegd.
     ✔  HRD-locatie punten al uitgelezen.
     ✔  Uittredepunten al toegevoegd.
     ✔  Polderpeil al toegevoegd.
     ✔  Binnenteenlijn al toegevoegd.
     ✔  Buitenteenlijn al toegevoegd.
     ✔  Intredelijn al toegevoegd.
     ✔  Gebruikersgedefinieerde GIS invoer (2 stuks): top_zand, D_wvp.

    GEOGRAFISCHE KOPPELINGEN
     ✔  HRD-locaties al gekoppeld aan uittredepunten.
     ✔  Afstanden intrede, buitenteen en binnenteen al gekoppeld aan uittredepunten.
     ✔  Polderpeil al gekoppeld aan uittredepunten.
     ✔  Afstand en metrering tot reflijn al gekoppeld aan uittredepunten.
     ✔  Vakken al gekoppeld aan uittredepunten.

    HANDMATIGE INVOER
     ✔  Excel-sheet ingeladen.


De gebruiker kiest welk belastingmodel gebruikt wordt. Momenteel zijn dit of model4a of de stijghoogte o.b.v. respons.
Paragraaf <<verwijzing aanmaken>> gaat hier verder op in. Daarnaast kan de gebruiker kiezen welke verschalingsfactoren
worden toegepast. Dit zijn onder andere de getijdezandfactor en 3D verschaling. Dit is toegelicht in paragraaf
<<verwijzing aanmaken>>.

In het onderdeel 'GIS lagen' wordt de gebruiker gevraagd de geografische data in te laden. Dit zijn onder andere het
dijktraject, de vakindeling en de intredelijn. Omdat de gebruiker vaak zijn invoer al geografisch gekoppeld heeft is
gebruikersgedefinieerde GIS invoer ook mogelijk. Dit geeft je de vrijheid om van elke parameter geografisch gerefereerde
data in te laden. Het klikken en/of automatisch genereren van uittredepunten worden verder toegelicht in paragraaf
<<verwijzing aanmaken>>.

Na het inladen van de geografische data wordt dit automatisch gekoppeld aan de uittredepunten en vakken.

Tot slot verzoekt de applicatie je om de resterende invoer te definiëren in een Excel template.


.. TODO: Verwijzingen aanmaken.


Rekenmodel
~~~~~~~~~~

Er zijn enkele algemene instellingen, dit is hoofdzakelijk de systeem keuze. Momenteel is enkel `Piping`` een keuze.
Later wordt dit uitgewerkt naar onder andere de keuzes ``model4a`` en deze i.c.m. Moria en/of het toepassen van
respons.

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
