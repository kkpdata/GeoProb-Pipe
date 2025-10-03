Uittredepuntenmethode
=====================

Wat is de uittredepuntenmethode?
--------------------------------

Conform de handleiding overstromingskansanalyse :cite:t:`HOVK_STPH_2024` en de eerdere schematiseringshandleidingen :cite:t:`sh_piping_2021` wordt een dijktraject opgedeeld in dijkvakken. Per dijkvak is de veronderstelling dat er sprake is van (statistische) homogeniteit. Dit betekent dat alle uitgangspunten uitgangspunten min of meer gelijk zijn over het dijkvak. 
Per dijkvak wordt gewoonlijk één doorsnede gekozen die representatief is voor het dijkvak. 
Op voorhand is echter niet bekend waar de zwakste plek in het dijkvak zich bevindt. De uittredepuntenmethode probeert dit probleem op te lossen door binnen een dijkvak meerdere mogelijke uittredepunten te definiëren. Deze uittredepunten kan je zien als doorsneden. Met deze methode kan relatief gemakkelijk veel uittredepunten (doorsneden) doorgerekend worden. Door een veelvoud aan berekende uittredepunten ontstaat een gebiedsdekkend beeld van het risico op piping.

De uitkomst van de (probabilistische) som bepaalt welk uittredepunt de grootste bijdrage heeft aan de faalkans van het dijkvak.

Hoe werkt de uittredepuntenmethode?
-----------------------------------

De rekenmethodiek volgt de schematiseringshandleiding :cite:t:`sh_piping_2021` en de handleiding overstromingskansanalyse :cite:t:`HOVK_STPH_2024`, echter met een aantal belangrijke aanvullingen:

* Per dijkvak worden meerdere uittredepunten gedefinieerd. Deze uittredepunten worden zodanig gekozen dat ze een goede dekking geven van het dijkvak.
* Elk uittredepunt kent zijn eigen (unieke) combinatie van uitgangspunten. Geometrische uitgangspunten zoals maaiveldniveau, aftstand tot de buitenteen en belastingen worden gekoppeld aan de locatie van het uittredepunt.
* Eigenschappen van de ondergrond worden, afhankelijk van de beschikbare data, op verschillende manieren gekoppeld aan de uittredepunten. Dit kan zijn door uitgangspunten op vakniveau te definiëren, of door gebruik van grids.
* Het combineren van de verschillende uitgangspunten heeft tot doel om een passende schematisatie per uittredepunt te maken.



Meer informatie over de rekenmethodiek is te vinden in de :ref:`rekenmethodiek`.