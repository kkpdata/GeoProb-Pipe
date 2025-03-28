# open-stph

Het project open-stph werkt aan een piping rekenkernel in python en heeft tot doel om zowel semi-probabilistische als probabilistische scenarioberekeningen uit te voeren. Daarnaast ondersteunt het alle stappen om een beoordeling voor piping uit te voeren.

## Uittredepunten vs. dwarsdoorsneden

Piping is een ruimtelijk probleem. Door alle mogelijke uittredepunten te evalueren ontstaat een beeld waar de 'zwakke' plek in de waterkering is. Elk uittredepunt is in feite een dwarsdoorsnede. Door heel veel uittredepunten in een vak te evalueren, zijn er minder onzekerheden en worden fysiek onmogelijke combinaties van variabelen uitgesloten. 

## Procesbeschrijving

Het uitvoeren van berekening als deze is op te delen in een aantal stappen:

1. Pre-processing van de schematisatie
2. Uitvoeren van de berekeningen
3. Post-processing van de resultaten

Deze stappen zijn beschreven in [procesbeschrijving](docs/Procesbeschrijving.md).

## Beschrijving rekenkernel

De standaard rekenkernel van het WBI heeft geen koppeling tussen de respons van de stijghoogte in het watervoerende pakket en de Sellmeijer berekening. Daarom is er sprake van meerdere rekenkernels. Dit project richt zich in eerste instantie op integratie met het analytische grondwatermodel 4a van het Technisch Rapport Waterspanningen bij dijken.

De [beschrijving van de rekenkernel](docs/Beschrijving_rekenkernel.md) staat hier.