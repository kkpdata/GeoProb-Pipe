# Procesbeschrijving

Deze procesbeschrijving gaat uit van de uittredepuntenmethode in combinatie met het analytische stijghoogtemodel model 4a.

## Pre Processing
### Vastleggen algemene uitgangspunten van de berekening


### Vastleggen uittredepunten

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

#### Discussie

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