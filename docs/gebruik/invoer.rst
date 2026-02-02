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
Het proces van parameterinvoer vraagt om enige toelichting, omdat het iteratief van aard is. De invoer van parameters
verloopt via een Excel‑bestand dat in GeoProb‑Pipe wordt geïmporteerd. Binnen dit bestand kunnen parameters op
verschillende hiërarchische niveaus worden gespecificeerd:

- Trajectniveau
- Vakniveau
- Vakniveau per ondergrondscenario
- Uittredepuntniveau

Wanneer voor een parameter zowel geografische invoer als Excel‑invoer beschikbaar is, heeft de Excel‑invoer voorrang
en wordt de geografische invoer overschreven.

Het voordeel van invoer op verschillende niveaus is dat je GeoProb-Pipe eerst globaal kunt vullen op trajectniveau,
vervolgens de berekeningen kunt uitvoeren en daarna — op basis van de resultaten — de invoer verder kunt verfijnen op
lagere niveaus zoals vakniveau. Dit maakt het proces iteratief: je specificeert steeds meer detail naarmate het oordeel
verder moet worden aangescherpt.

Onder de motorkap doorzoekt GeoProb‑Pipe deze niveaus hiërarchisch. Als op een lager niveau geen invoer beschikbaar is,
kijkt het programma automatisch naar het eerstvolgende hogere niveau. Wanneer er bijvoorbeeld geen invoer is op
vakniveau, wordt automatisch gecontroleerd of er invoer op trajectniveau aanwezig is. Hierdoor hoef je alleen invoer
op te geven voor de vakken, scenario’s of uittredepunten waarvoor je daadwerkelijk een nadere detaillering wilt
doorvoeren.

In de onderstaande figuur staat een voorbeeld van hoe invoer op de verschillende niveaus wordt toegepast.

[[TODO: Figuur toevoegen]]

.. TODO: Waar beschrijven we hoe parameter invoer elkaar kan overlappen?

Keuze menu 'Parameter invoer'
"""""""""""""""""""""""""""""
De volgende keuze opties zijn er:

 - Zijn de invoer tabellen zijn naar wens? Ga door naar volgende stap
 - Overzichtsfiguren van invoertabellen: Exporteren

De overzichtsfiguren bieden middels HTML-figuren een interactieve manier om snel visueel te zien hoe de invoer van je
parameters is gedaan. Je krijgt een figuur per parameter.

 - Invoer tabellen: Importeren vanuit Excel
 - Invoer tabellen: Exporteren naar Excel


Beschrijving specifieke parameters
""""""""""""""""""""""""""""""""""
Een beschrijving van de invoerparameters staat :ref:`hier<stijghoogtemodellen-geoprob>` beschreven.

.. TODO: Moeten we wel verwijzen naar de geohydrologische modellen? Er is nog een bovenliggende model Piping zelf.
    Daar naar verwijzen, waarna die wel weer doorverwijst naar de geohydrologische modellen?






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
