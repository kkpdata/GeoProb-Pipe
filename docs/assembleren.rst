Assembleren
===========

Deze pagina beschrijft de assemblage van faalkansen binnen GeoProb-Pipe voor het faalmechanisme STPH (piping). 
De verschillende pagina’s binnen dit hoofdstuk beschrijven 
hoe lokaal berekende faalkansen worden opgebouwd vanaf scenarioberekeningen en uiteindelijk worden vertaald naar een trajectkans.

De assemblage start altijd op scenarioniveau. Per uittredepunt worden meerdere ondergrondscenario’s en faalmechanismen probabilistisch doorgerekend, 
wat resulteert in een set scenariofaalkansen. Deze worden vervolgens samengevoegd tot een representatieve faalkans op uittredepuntniveau.

Vanaf dit punt verschillen de methoden in de manier waarop de stap naar trajectniveau wordt gemaakt. Er wordt geen uniforme of verplichte vakindeling gehanteerd. 
Afhankelijk van de gekozen methode wordt de trajectkans direct bepaald of via een tussenvorm benaderd.


.. toctree::
   :maxdepth: 2
   :caption: Inhoud
   :titlesonly:
    
   assembleren/kader
   assembleren/stap0_sc
   assembleren/stap1_sc_up
   assembleren/vakkans_trajectkans
   assembleren/methoden_trajectkans
   assembleren/resultaten
   