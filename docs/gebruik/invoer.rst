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
Er is één algemeen item in het invoerproces, namelijk de keuze van het geohydrologische model. Deze keuze bepaalt welke
invoervariabelen nodig zijn om pipingberekeningen uit te voeren. Het geohydrologische model legt de relatie vast tussen
de stijghoogte in het uittredepunt en de overige geohydrologische variabelen zoals bijvoorbeeld door transmissiviteit 
van het zandpakket. Momenteel zijn 3 modellen ingebouwd, waaronder het veel gebruikte model 4A. Een gedetailleerde
beschrijving van deze modellen vind je :ref:`hier<stijghoogtemodellen-geoprob>`.


GIS lagen & Geografische koppelingen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In het onderdeel 'GIS lagen' wordt de gebruiker gevraagd om verschillende geografische datasets te importeren. Dit
betreft onder andere het dijktraject, de vakindeling, de uittredepunten en de intredelijn. Gegevens kunnen worden
ingelezen vanuit een Shapefile, GeoDatabase of GeoPackage. Omdat je de applicatie op elk moment kunt afsluiten, kun je 
ook eerst een deel van de GIS-data importeren en later verder gaan. Omdat `GeoProp-Pipe` een GeoPackage is, 
kan je alle geïmporteerde data in ArcGIS/Qgis bekijken en controleren of het goed is geïmporteerd.


Na het importeren van de geografische data worden de benodigde geografische koppelingen automatisch gelegd. Deze 
geografische koppelingen bestaan uit de kortste afstand tussen 2 objecten (bijvoorbeeld afstand tot de intredelijn) of 
het uitlezen van de attribuutwaarde op de locatie van het uittredepunt (bijvoorbeeld het polderpeil). Deze koppelingen 
worden automatisch gelegd.

Parameter invoer
^^^^^^^^^^^^^^^^
Het proces van parameterinvoer vraagt om enige toelichting omdat het gebruik maakt van een hiërarchisch systeem. 
De invoer van parameters verloopt via een Excel‑bestand dat in GeoProb‑Pipe wordt geïmporteerd. 
Binnen dit bestand kunnen parameters op verschillende hiërarchische niveaus worden gespecificeerd:

- Trajectniveau
- Vakniveau
- Vakniveau per ondergrondscenario
- Uittredepuntniveau

Wanneer voor een parameter zowel geografische invoer als Excel‑invoer beschikbaar is, heeft de Excel‑invoer voorrang
en wordt de geografische invoer overschreven.

Het voordeel van invoer op verschillende niveaus is dat je GeoProb-Pipe eerst globaal kunt vullen op trajectniveau,
vervolgens de berekeningen kunt uitvoeren en daarna — op basis van de resultaten — de invoer verder kunt verfijnen op
lagere niveaus zoals vakniveau of ondergrondscenario. Dit maakt het proces iteratief en efficiënt: het oordeel bepaalt 
het noodzakelijke detailniveau van de invoer. 

Onder de motorkap doorzoekt GeoProb‑Pipe deze niveaus hiërarchisch. Als op een lager niveau geen invoer beschikbaar is,
kijkt het programma automatisch naar het eerstvolgende hogere niveau. Wanneer er bijvoorbeeld geen invoer is op
vakniveau, wordt automatisch gecontroleerd of er invoer op trajectniveau aanwezig is. Hierdoor hoef je alleen invoer
op te geven voor de vakken, scenario’s of uittredepunten waarvoor je daadwerkelijk een nadere detaillering wilt
doorvoeren.

.. TODO: figuur toevoegen van hiërarchische systeem van parameterinvoer. Hierin ook aangeven dat de invoer op een 
   hoger niveau de invoer op een lager niveau overschrijft.

.. TODO: Waar beschrijven we hoe parameter invoer elkaar kan overlappen?

Keuze menu 'Parameter invoer'
"""""""""""""""""""""""""""""
Als alle parameters zijn ingevoerd, zijn de volgende keuze opties beschikbaar:

 - Zijn de invoer tabellen zijn naar wens? Ga door naar volgende stap
 - Overzichtsfiguren van invoertabellen: Exporteren

De overzichtsfiguren bieden middels HTML-figuren een interactieve manier om snel visueel te zien hoe de invoer van je
parameters is gedaan. Je krijgt een figuur per parameter.

 - Invoer tabellen: Importeren vanuit Excel
 - Invoer tabellen: Exporteren naar Excel


Beschrijving specifieke parameters
""""""""""""""""""""""""""""""""""
Elk geohydrologisch model heeft specifieke invoerparameters. Een beschrijving van de 
invoerparameters staat :ref:`hier<stijghoogtemodellen-geoprob>` beschreven.

.. TODO: Moeten we wel verwijzen naar de geohydrologische modellen? Er is nog een bovenliggende model Piping zelf.
    Daar naar verwijzen, waarna die wel weer doorverwijst naar de geohydrologische modellen?

