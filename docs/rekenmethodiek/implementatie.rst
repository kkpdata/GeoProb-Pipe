Implementatie
=============

De implementatie van de rekenmethodiek is modulair opgebouwd en bestaat uit drie samenhangende onderdelen:

1.  **Fysische componenten**
    In deze stap worden de geohydrologische en geotechnische componenten berekend die de fysieke toestand van het
    systeem beschrijven, zoals de deklaagdikte, heave-gradiënt, kwelweglengte en het kritieke verval volgens
    Sellmeijer.
    Deze berekeningen zijn geïmplementeerd in het subpackage ``geoprob_pipe.calculations.physical_components.piping``.
    De fysische componenten vormen de bouwstenen voor de grenstoestandsfuncties. Ze zijn onafhankelijk van het
    gekozen stijghoogtemodel: ongeacht of de stijghoogte wordt bepaald met het analytische model 4A of een numeriek
    model worden dezelfde fysische componenten toegepast.

2.  **Grenstoestandsfuncties**
    De grenstoestandsfuncties beschrijven de drie deelmechanismen die leiden tot piping:
    *opbarsten*, *heave* en *terugschrijdende erosie*.
    Voor elk mechanisme wordt een aparte grenstoestandsfunctie berekend, waarna de gecombineerde toestand wordt
    bepaald. In de implementatie is dit voor elk stijghoogtemodel één functie. Deze functie geeft als resultaat
    alle grenstoestandsfuncties, ook de gecombineerde.
    De grenstoestandsfuncties maken gebruik van de fysische componenten uit stap 1.
    Elke implementatie van een stijghoogtemodel wordt aangeroepen via een eigen functie in de subpackage
    ``geoprob_pipe.calculations`` (bijvoorbeeld ``limit_state_model4a`` of ``limit_state_moria``).
    Deze functies combineren de fysische componenten en grenstoestandsfuncties tot één consistente berekening van
    de faalkans per uittredepunt.

3.  **Stijghoogtemodellen**
    Het stijghoogtemodel bepaalt de stijghoogte in het uittredepunt (:math:`\phi_{exit}`) en vormt daarmee de
    koppeling tussen de hydraulische belasting (buitenwaterstand, polderpeil) en de ondergrondrespons.
    `GeoProb-Pipe` ondersteunt meerdere typen stijghoogtemodellen:
    - de WBI-formulering van de stijghoogte met een vaste responsfactor en kwelweglengte;
    - het analytische grondwatermodel *4A* op doorsnedeiveau;
    - resultaten van numerieke rastermodellen zoals *MORIA*;
    - en toekomstige uitbreidingen (bijv. TTIM) die via dezelfde interface kunnen worden toegevoegd.
