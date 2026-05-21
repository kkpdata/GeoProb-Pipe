Assembleren
===========

De faalkans voor het faalmechanisme STPH (piping) van een dijktraject bestaat uit een seriesysteem van uittredepunten, 
waarbij falen optreedt zodra één van de uittredepunten faalt. De trajectkans wordt mede bepaald door een onderlinge 
afhankelijkheid tussen uittredepunten. 
Deze probabilistische rekentechnieken zijn beschikbaar maar beperkt toegankelijk en rekenintensief, waardoor dit nog 
niet is geïmplementeerd in GeoProb-Pipe.

Als alternatief zijn er verschillende methoden ontwikkeld om de trajectkans te benaderen, rekening houdend  met de 
veronderstelde lengte-effecten. Dit wordt ook wel assembleren genoemd. Deze assemblage van faalkansen is o.a. beschreven op de bottom-up assemblage door
het Adviesteam Dijkontwerp in Rode Draad #10 :cite:`ADO2024Assembleren`.

Deze sectie beschrijft de verschillende methoden die in GeoProb-Pipe zijn geïmplementeerd om de trajectkans te benaderen.
Per onderdeel is aangegeven welke aannames er zijn gedaan om de methode toe te kunnen passen.

De beschrijving start op scenarioniveau met de berekeningen die leiden tot een betrouwbaarheid van een enkele 
scenarioberekening en eindigt bij de benadering van de trajectkans. DIt is opgedeeld in de volgende stappen:

1. **Stap 0: Bepalen faalkans op scenarioniveau**
2. **Stap 1: Bepalen faalkans per uittredepunt**
3. **Stap 2: Methoden die de trajectkans benaderen**



.. toctree::
   :maxdepth: 2
   :caption: Inhoud
   :titlesonly:
    
   .. assembleren/kader
   
   assembleren/stap0_sc
   assembleren/stap1_sc_up
   assembleren/stap2_vakkans_trajectkans
   assembleren/resultaten
   