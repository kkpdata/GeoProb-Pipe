.. _rekenmethodiek:


.. TODO: Ik vind deze pagina onduidelijk ingedeeld. Kunnen we het volgende voorstel bespreken?
    Rekenmethodiek
        Berekeningsmodel
        Stijghoogtemodellen
            standaard WBI model
            Model 4a
            Numeriek stijghoogtemodel
        Modelfactoren
            relatie met beslisraamwerk: welke factoren zijn er geimplementeerd?
            Getijdezandfactor
            3D verschaling
            Gebruikersgedefinieerde factoren


Rekenmethodiek
==============


.. contents::
   :local:
   :depth: 3


Rekenmethodiek
==============

Deze pagina beschrijft de rekenmethodiek die `GeoProb-Pipe` gebruikt voor het berekenen van de totale faalkans op piping per uittredepunt.

Implementatie
-------------

De implementatie van de rekenmethodiek is modulair opgebouwd en bestaat uit drie samenhangende onderdelen:

1. **Fysische componenten**
   In deze stap worden de geohydrologische en geotechnische componenten berekend die de fysieke toestand van het systeem beschrijven,
   zoals de deklaagdikte, heave-gradiënt, kwelweglengte en het kritieke verval volgens Sellmeijer.
   Deze berekeningen zijn geïmplementeerd in het subpakket ``geoprob_pipe.calculations.physical_components.piping``
   De fysische componenten vormen de bouwstenen voor de grenstoestandsfuncties.
   Ze zijn onafhankelijk van het gekozen stijghoogtemodel: ongeacht of de stijghoogte wordt bepaald met het analytische model 4A of een numeriek model worden dezelfde fysische componenten toegepast.

2. **Grenstoestandsfuncties**
   De grenstoestandfuncties beschrijven de drie deelmechanismen die leiden tot piping:
   *opbarsten*, *heave* en *terugschrijdende erosie*.
   Voor elk mechanisme wordt een aparte grenstoestandsfunctie berekend, waarna de gecombineerde toestand wordt bepaald.
   In de implementatie is dit voor elk stijghoogtemodel één functie. Deze functie geeft als resultaat alle grenstoestandfuncties, ook de gecombineerde.
   De grenstoestandsfuncties maken gebruik van de fysische componenten uit stap 1.
   Elke implementatie van een stijghoogtemodel wordt aangeroepen via een eigen functie in het pakket ``geoprob_pipe.calculations`` (bijvoorbeeld ``limit_state_model4a`` of ``limit_state_moria``).
   Deze functies combineren de fysische componenten en grenstoestandsfuncties tot één consistente berekening van de faalkans per uittredepunt.

3. **Stijghoogtemodellen**
   Het stijghoogtemodel bepaalt de stijghoogte in het uittredepunt (:math:`\phi_{exit}`) en vormt daarmee de koppeling tussen
   de hydraulische belasting (buitenwaterstand, polderpeil) en de ondergrondrespons.
   `GeoProb-Pipe` ondersteunt meerdere typen stijghoogtemodellen:
   - de WBI-formulering van de stijghoogte met een vaste responsfactor en kwelweglengte;
   - het analytische grondwatermodel *4A* op doorsnedeniveau;
   - resultaten van numerieke rastermodellen zoals *MORIA*;
   - en toekomstige uitbreidingen (bijv. TTIM) die via dezelfde interface kunnen worden toegevoegd.


Faalpad en foutenboom piping
----------------------------

In :numref:`faalpad-STPH` zie je een veelvoorkomend faalpad voor het faalmechanisme *piping* :cite:`HOVK_STPH_2024`.
`GeoProb-Pipe` richt zich op het modelleren van de initiële mechanismen die leiden tot piping: opbarsten, heave en terugschrijdende erosie.
Hierbij wordt aangenomen dat piping optreedt wanneer de deklaag opbarst, heave optreedt en er doorgaande terugschrijdende erosie plaatsvindt.
In de schematiseringshandleiding piping :cite:`sh_piping_2021` zijn de bijbehorende grenstoestandsfuncties beschreven die in het BOI en in `GeoProb-Pipe` worden gebruikt.

.. _faalpad-STPH:

.. figure:: _static/faalpad_piping.png
   :alt: Veelvoorkomend faalpad voor het faalmechanisme piping.
   :align: center

   Veelvoorkomend faalpad voor het faalmechanisme *piping* :cite:`HOVK_STPH_2024`.

.. TODO: Foutenboom toevoegen als plaatje?

Basis grenstoestandfuncties BOI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
De onderstaande grenstoestandsfuncties vormen de kern van de berekening in `GeoProb-Pipe`.
Ze worden identiek toegepast in elk stijghoogtemodel (`limit_state_wbi`, `limit_state_model4a`, `limit_state_moria`).
De verschillen tussen de modellen zitten uitsluitend in de berekening van de stijghoogte :math:`\phi_{exit}` en bijbehorende parameters.

Opbarsten
^^^^^^^^^

De grenstoestandfunctie van **opbarsten** :math:`Z_{u}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{u} = m_{u} \cdot \Delta \phi_{c,u} - (\phi_{exit} - h_{exit})

waarbij :math:`m_{u}` de modelfactor voor opbarsten is [-]. 

De grenspotentiaal ten opzichte van maaiveldniveau :math:`\Delta \phi_{c,u}` [m] wordt bepaald door het effectieve gewicht van de deklaag onder water:

.. math::

   \Delta \phi_{c,u} = \frac{d_{deklaag} \cdot (\gamma_{sat,deklaag} - \gamma_{w})}{\gamma_{w}}

waarin:

- :math:`d_{deklaag}` de dikte van de deklaag is [m]
- :math:`\gamma_{sat}` het gemiddeld verzadigd volumegewicht van de cohesieve deklaag is [kN/m³]
- :math:`\gamma_{w}` het volumegewicht van water is [kN/m³]

De dikte van de deklaag :math:`d_{deklaag}` ter plaatse van het uittredepunt is gedefinieerd als de verticale afstand tussen het maaiveldniveau en de bovenkant van de pipinggevoelige zandlaag:

.. math::

   d_{deklaag} = mv_{exit} - top_{zandlaag}

waarin:
- :math:`mv_{exit}` maaiveldniveau ter plaatse van het uittredepunt [m+NAP]
- :math:`top_{zandlaag}` niveau bovenkant van de pipinggevoelige zandlaag [m+NAP]

De stijghoogte ter plaatse van het uittredepunt :math:`\phi_{exit}` [m+NAP] wordt volgens de schematiseringshandleiding :cite:`sh_piping_2021` beschreven door:

.. math::

   \phi_{exit} = \phi_{polder} + r_{exit} \cdot (h_{rivier} - \phi_{polder})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]
- :math:`r_{exit}` de dempingsfactor ter plaatse van het uittredepunt [-]
- :math:`h_{rivier}` het waterniveau in de rivier [m+NAP]

De dempingsfactor :math:`r_{exit}` ter plaatse van het uittredepunt is afhankelijk van de locatie van het uittredepunt ten opzichte van de dijk en de geohydrologische situatie. De schematiseringshandleiding piping :cite:`sh_piping_2021` hanteert dit als een onafhankelijke invoerparameter.

:math:`h_{exit}` is de randvoorwaarde in het uittredepunt, gedefinieerd door het maximum van het polderpeil en het maaiveldniveau ter plaatse van het uittredepunt:

.. math::

   h_{exit} = max(\phi_{polder}, mv_{exit})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]


Heave
^^^^^

De grenstoestandfunctie van **heave** :math:`Z_{h}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{h} = m_{h} \cdot i_{i,c} - \frac{\phi_{exit} - h_{exit}}{d_{deklaag}}

waarin:

- :math:`m_{h}` de modelfactor voor heave is [-]
- :math:`i_{i,c}` de kritieke heave-gradiënt is [-]

Opgemerkt wordt dat de modelfactoren :math:`m_{u}` en :math:`m_{h}` niet zijn opgenomen in de formules van de schematiseringshandleiding piping :cite:`sh_piping_2021`, maar wel in deze implementatie zijn opgenomen om de modelonzekerheid expliciet te kunnen kwantificeren.


Terugschrijdende erosie
^^^^^^^^^^^^^^^^^^^^^^^^

De grenstoestandfunctie van **terugschrijdende erosie** :math:`Z_{p}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{p} = m_{p} \cdot \Delta H_{c} - \Delta h_{red}

met :math:`\Delta h_{red}` het gereduceerde verval over de deklaag [m] als:

.. math::
   
   \Delta h_{red} = h_{buitenwaterstand} - h_{exit} - r_{c,deklaag} \cdot d_{deklaag}

waarin:

- :math:`m_{p}` de modelfactor voor terugschrijdende erosie is [-]
- :math:`\Delta H_{c}` het kritieke verval over de deklaag is [m]
- :math:`h_{buitenwaterstand}` de buitenwaterstand is [m+NAP]
- :math:`h_{exit}` de randvoorwaarde in het uittredepunt is [m+NAP]
- :math:`r_{c,deklaag}` de reductieconstante van het verval over de deklaag is [-]
- :math:`d_{deklaag}` de dikte van de deklaag is [m]

 Het kritieke verval over de deklaag :math:`\Delta H_{c}` is gebaseerd op het in 2011 aangepaste model van Sellmeijer.

 .. math::

   \Delta H_{c} = L_{kwelweg} \cdot F_{resistance} \cdot F_{scale} \cdot F_{geometry}

met:

.. math::

   F_{resistance} = \eta \frac{\gamma_{korrel} - \gamma_{w}}{\gamma_{w}} \cdot tan(\theta)

   F_{scale} = \frac{d_{70,m}}{\sqrt[3]{L_{kwelweg} \cdot \frac{k \cdot \upsilon_{w}}{g}}} \left(\frac{d_{70}}{d_{70,m}} \right)^{0.4}

   F_{geometry} = 0.91 \left(\frac{D_{wvp}}{L_{kwelweg}} \right)^{\frac{0.28}{\left(\frac{D_{wvp}}{L_{kwelweg}} \right)^{2.8} - 1} + 0.04}


waarin:

- :math:`L_{kwelweg}` de kwelweglengte is [m], gedefinieerd als de horizontale afstand tussen het uittredepunt en een onzeker intredepunt.
- :math:`\eta` coëfficiënt van White (sleepkrachtfactor) [-]. Standaardwaarde is 0.25
- :math:`\gamma_{korrel}` volumieke dichtheid van zand [kN/m³]. Standaardwaarde is 26.0 kN/m³
- :math:`\gamma_{w}` het volumegewicht van water [kN/m³]
- :math:`\theta` de rolweerstandshoek van zandkorrels van de aangepaste Sellmeijer-rekenregel [°]. Standaardwaarde is 37°
- :math:`d_{70,m}` de referentie- :math:`d_{70}`-waarde [m]. Standaardwaarde is 2.08E-4 m
- :math:`d_{70}` de 70-percentielwaarde van de korrelverdeling van de pipinggevoelige laag [m]
- :math:`k` de Darcy-doorlatendheid van de zandlaag [m/s]
- :math:`\upsilon_{w}` de kinematische viscositeit van water [m²/s]. Standaardwaarde is 1.33E-6 m²/s bij 10°C
- :math:`g` de zwaartekrachtversnelling [m/s²]. Standaardwaarde is 9.81 m/s²
- :math:`D_{wvp}` de dikte van de watervoerende zandlaag [m]

.. _stijghoogtemodellen-geoprob:

Stijghoogtemodellen in GeoProb-Pipe
-----------------------------------

De berekening van de stijghoogte :math:`\phi_{exit}` wordt uitgevoerd binnen de limit-state functies,
waarbij elke functie een specifiek type stijghoogtemodel aanroept:

- ``limit_state_wbi`` – eenvoudige benadering met vaste responsfactor;
- ``limit_state_model4a`` – analytisch grondwatermodel 4A (doorsnede);
- ``limit_state_moria`` – numeriek rastermodel (zoals het regionale grondwatermodel MORIA).

De rekenmethodiek is zodanig opgezet dat in de toekomst ook andere stijghoogtemodellen kunnen worden toegevoegd.

.. _model4a:

Analytische stijghoogtemodel 4A
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Het analytische grondwatermodel *4A* vormt één van de mogelijke implementaties van het stijghoogtemodel
(*stap 3* van de rekenmethodiek).
Dit model beschrijft de stroming van grondwater door de zandlaag onder een dijk op basis van stationaire,
lineaire stroming in doorsnedeniveau.
De overige fysische componenten en grenstoestandsfuncties worden op identieke wijze berekend als bij andere
stijghoogtemodellen; alleen de bepaling van de stijghoogte :math:`\phi_{exit}` en de responsfactor :math:`r_{exit}`
verschilt.

De grondwaterstroming vormt de drijvende kracht achter het proces van terugschrijdende erosie.
Door het analytische grondwatermodel 4A van :cite:`trw_2004` toe te passen,
kan de respons :math:`r_{exit}` in het uittredepunt worden beschreven als functie van de locatie in het
dwarspofiel :math:`x_{exit}` [m] en de geohydrologische parameters van model 4A.
Een uitgebreide toelichting op de onderliggende theorie van dit model is te vinden in :ref:`stationair-model`.

De respons in het uittredepunt wordt bepaald met:
.. math::

   r_{exit}(x) = f(x_{exit}, L_1, L_2, L_3, c_{voorland}, c_{achterland}, k, D_{wvp})

Geometrische parameters
^^^^^^^^^^^^^^^^^^^^^^^
Geometrische parameters :math:`L_1` en :math:`L_2` zijn omgeschreven naar afstanden ten opzichte van het uittredepunt:

.. math::

   L_1 = L_{intrede} - L_{but}

   L_2 = L_{but} - L_{bit}

waarin:

- :math:`L_{intrede}` de afstand van het uittredepunt tot een geometrische intredelijn [m]
- :math:`L_{but}` de afstand van het uittredepunt tot de buitenteen [m]
- :math:`L_{bit}` de afstand van het uittredepunt tot de binnenteen [m]
- :math:`L_3` de achterlandlengte [m]
- :math:`x_{exit}` de afstand van het uittredepunt tot de binnenteen [m]. De aanname is dat uittredepunten altijd binnendijks van een (denkbeeldige) binnenteen liggen.
- :math:`c_{voorland}` de weerstand van de deklaag in het voorland [dag]
- :math:`c_{achterland}` de weerstand van de deklaag in het achterland [dag]


Effectieve voorlandlengte
^^^^^^^^^^^^^^^^^^^^^^^^^
De kwelweglengte :math:`L_{kwelweg}` maakt conform de schematiseringshandleiding piping :cite:`sh_piping_2021` gebruik van het principe van de effectieve voorlandlengte.

.. math::

   L_{kwelweg} = L_{but} + L_{eff,voorland}

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   \lambda_{1} = \sqrt{c_{voorland} \cdot k \cdot D_{wvp}}

waarin:

- :math:`L_{eff,voorland}` de effectieve voorlandlengte is [m]
- :math:`\lambda_{1}` de spreidingslengte van het voorland is [m]
- :math:`\c` is de deklaagdikte gedeeld door de doorlatendheid van de deklaag [dag]

Overzicht parameters model 4A
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Het berekeningsmodel met het analytische grondwatermodel 4A kent de volgende invoerparameters:

.. list-table:: Invoerparameters berekeningsmodel met model 4A
   :widths: 20 60 20
   :header-rows: 1

   * - Variable
     - Omschrijving
     - Verdeling/Constante
   * - :math:`h_{buitenwaterstand}`
     - Buitenwaterstand [m+NAP]
     - CDF
   * - :math:`\phi_{polder}`
     - Waterniveau in de polder [m+NAP]
     - deterministisch
   * - :math:`mv_{exit}`
     - Maaiveldniveau ter plaatse van uittredepunt [m+NAP]
     - deterministisch
   * - :math:`r_{c,deklaag}`
     - Reductieconstante van het verval over de deklaag [-]
     - lognormaal
   * - :math:`L_{bit}`
     - Afstand van het uittredepunt tot de binnenteen [m]
     - deterministisch
   * - :math:`L_{but}`
     - Afstand van het uittredepunt tot de buitenteen [m]
     - deterministisch
   * - :math:`L_{intrede}`
     - Afstand van het uittredepunt tot geometrische intredelijn [m]
     - deterministisch
   * - :math:`L_{3}`
     - Achterlandlengte [m]
     - deterministisch
   * - :math:`top_{zandlaag}`
     - niveau bovenkant van de pipinggevoelige zandlaag [m+NAP]
     - normaal
   * - :math:`c_{voorland}`
     - Weerstand van de deklaag in het voorland [dag]
     - lognormaal
   * - :math:`c_{achterland}`
     - Weerstand van de deklaag in het achterland [dag]
     - lognormaal
   * - :math:`D_{wvp}`
     - Dikte van de watervoerende zandlaag [m]
     - lognormaal
   * - :math:`kD_{wvp}`
     - Transmissiviteit van het watervoerende pakket [m²/dag]
     - lognormaal
   * - :math:`d_{70}`
     - 70-percentielwaarde van de korrelverdeling van de pipinggevoelige laag [m]
     - lognormaal
   * - :math:`\gamma_{sat,deklaag}`
     - Gemiddeld verzadigd volumegewicht deklaag [kN/m³]
     - lognormaal, shift = 10.0
   * - :math:`i_{i,c}`
     - Kritieke heave gradiënt [-]
     - lognormaal
   * - :math:`d_{70,m}`
     - Referentiewaarde voor de :math:`d_{70}` [m]
     - 2.08E-4 m
   * - :math:`\upsilon_{w}`
     - Kinematische viscositeit van water [m²/s]
     - 1.33E-6 m²/s bij 10°C
   * - :math:`\eta`
     - Coëfficiënt van White (sleepkrachtfactor) [-]
     - 0.25
   * - :math:`\theta`
     - Rolweerstandshoek van zandkorrels van de aangepaste Sellmeijer rekenregel [°]
     - 37°    
   * - :math:`g`
     - Zwaartekrachtversnelling [m/s²]
     - 9.81 m/s²
   * - :math:`\gamma_{korrel}`
     - Volumieke dichtheid zand [kN/m³]
     - 26.0 kN/m³
   * - :math:`\gamma_{w}`
     - Volumegewicht van water [kN/m³]
     - 9.81 kN/m³
   * - :math:`m_{u}`
     - Modelfactor opbarsten [-]
     - normaal
   * - :math:`m_{h}`
     - Modelfactor heave [-]
     - normaal
   * - :math:`m_{p}`
     - Modelfactor terugschrijdende erosie [-]
     - normaal

Numerieke stijghoogtemodellen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Het numerieke stijghoogtemodel vormt een tweede implementatie van het stijghoogtemodel (*stap 3* van de rekenmethodiek).
In dit geval wordt de stijghoogte :math:`\phi_{exit}` niet analytisch berekend, maar afgeleid uit een numeriek grondwatermodel
dat de ruimtelijke variatie in stijghoogten expliciet beschrijft.
De overige fysische componenten en grenstoestandsfuncties worden op identieke wijze berekend als bij het analytische model 4A;
alleen de bepaling van de stijghoogte, responsfactor en kwelweglengte verschilt.

Een numeriek stijghoogtemodel, zoals het regionale grondwatermodel MORIA van Waterschap Rivierenland,
levert informatie in de vorm van raster-bestanden.
Per uittredepunt kunnen hieruit de relevante geohydrologische parameters worden afgeleid.
De volgende variabelen worden uit het grid gelezen:

- :math:`\phi_{gemiddeld}(x,y)` een grid met het gemiddelde grondwaterstandniveau bij gemiddelde rivierwaterstand [m+NAP]
- :math:`h_{gemiddeld}` de gemiddelde rivierwaterstand nabij het uittredepunt [m+NAP]
- :math:`r_{exit}(x,y)` een grid met de respons in het uittredepunt [-]
- :math:`\lambda_{1}` de spreidingslengte van het voorland [m]

De stijghoogte in het uittredepunt wordt vervolgens bepaald met:

.. math::

   \phi_{exit}(x,y) = \phi_{gemiddeld}(x,y) + r_{exit}(x,y) \cdot (h_{buitenwaterstand} - h_{gemiddeld})

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   L_{kwelweg} = L_{but} + L_{eff,voorland}

Bespreken: moeten we nog een modelfactor :math:`m_{gw}` voor het stijghoogtemodel toevoegen.

Grenstoestandfuncties numeriek stijghoogtemodel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
De formules van de grenstoestandsfuncties zijn nu als volgt:

Grenstoestandfunctie opbarsten:

.. math::

   Z_{u} = m_{u} \cdot \Delta \phi_{c,u} - (\phi_{exit}(x,y) - h_{exit})

Grenstoestandfunctie heave:

.. math::

   Z_{h} = m_{h} \cdot i_{i,c} - \frac{\phi_{exit}(x,y) - h_{exit}}{d_{deklaag}}

Grenstoestandfunctie terugschrijdende erosie:

.. math::

   Z_{p} = m_{p} \cdot \Delta H_{c} - \Delta h_{red}

   \Delta h_{red} = h_{buitenwaterstand} - h_{exit} - r_{c,deklaag} \cdot d_{deklaag}

   L_{kwelweg} = L_{but} + L_{eff,voorland}

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   \lambda_{1} = \sqrt{c_{voorland} \cdot k \cdot D_{wvp}}


Correlatie tussen variabelen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
De beschrijving van het geohydrologische systeem met de variabelen betekent ook dat de onderlinge correlatie van de variabelen apart moet worden gedefinieerd. Dit betreft met name de correlatie tussen de spreidingslengte van het voorland :math:`\lambda_{1}` en de transmissiviteit van het watervoerende zandpakket :math:`kD` en in mindere mate de correlatie tussen de respons in het uittredepunt :math:`r_{exit}` en de transmissiviteit van het watervoerende zandpakket :math:`kD`. In het model 4A zijn deze correlaties modelmatig beschreven.

In het geval van een numeriek stijghoogtemodel is de correlatie tussen de spreidingslengte van het voorland en de transmissiviteit van het watervoerende zandpakket plaatsafhankelijk en wordt beschreven door het geohydrologische model.

Om een inschatting te doen van de correlatie tussen deze variabelen wordt een beperkte set van modelberekeningen uitgevoerd waarbij de transmissiviteit van het watervoerende pakket en de weerstand van het voorland wordt gevarieerd.
Voor elke berekening uit deze set wordt de spreidingslengte van het voorland afgeleid.
Gebruikelijk is het om daarbij per variabele 3 scenario's te hanteren (gemiddeld, -1.64 * sigma, +1.64 * sigma).
Voor 2 variabelen resulteert dit in 9 modelberekeningen.

Uit deze modelberekeningen wordt de gewogen correlatie tussen de transmissiviteit van het watervoerende pakket en de spreidingslengte van het voorland bepaald. Deze correlatie wordt vervolgens gebruikt in de probabilistische analyse.

Op basis van het model 4A is de correlatie tussen de transmissiviteit van het watervoerende pakket en de spreidingslengte van het voorland ongeveer 0.7, afhankelijk van de gekozen spreiding.
.. TODO: Ik vind deze nog lastig te plaatsen. @skapinga kun jij kijken hoe we deze binnen de structuur een betere plek kunnen geven?

Overzicht van implementaties in de code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. TODO: uiteindelijke implementatie controleren en tekst hierop aanpassen.
.. TODO: misschien de theorie (beschrijving grenstoestandsfuncties) en de implementatie (overzicht functies) beter scheiden?

In onderstaande tabel zijn de huidige implementaties van de stijghoogtemodellen binnen `GeoProb-Pipe` samengevat.
Elke implementatie volgt dezelfde structuur: eerst worden de fysische componenten berekend,
vervolgens de grenstoestandsfuncties, en tenslotte de gecombineerde limiettoestand.

.. list-table:: Overzicht van limit-state implementaties
   :widths: 20 25 35 20
   :header-rows: 1

   * - Functie
     - Beschrijving
     - Belangrijkste invoerparameters
     - Belangrijkste uitvoerwaarden

   * - ``limit_state_wbi``
     - Basismodel volgens WBI-formulering (met vaste responsfactor).
       Wordt gebruikt voor situaties zonder expliciet stijghoogtemodel.
     - :math:`L_{kwelweg}`, :math:`h_{buiten}`, :math:`\phi_{polder}`, :math:`r_{exit}`, :math:`d_{70}`, :math:`D_{wvp}`, :math:`\gamma_{sat,deklaag}`
     - :math:`Z_u`, :math:`Z_h`, :math:`Z_p`, :math:`Z_{combin}`, :math:`\phi_{exit}`, :math:`h_{exit}`

   * - ``limit_state_model4a``
     - Implementatie van het analytische grondwatermodel 4A (:cite:`trw_2004`).
       Berekening van respons :math:`r_{exit}` op basis van doorsnedemodel.
     - :math:`L_{intrede}`, :math:`L_{but}`, :math:`L_{bit}`, :math:`c_{voorland}`, :math:`c_{achterland}`, :math:`kD_{wvp}`, :math:`D_{wvp}`
     - :math:`Z_u`, :math:`Z_h`, :math:`Z_p`, :math:`Z_{combin}`, :math:`\phi_{exit}`, :math:`r_{exit}`, :math:`L_{kwelweg}`

   * - ``limit_state_moria``
     - Implementatie van een numeriek grondwatermodel (zoals MORIA).
       Gebruikt rasterinformatie voor de bepaling van :math:`\phi_{exit}` en :math:`r_{exit}`.
     - :math:`\phi_{gemiddeld}(x,y)`, :math:`h_{gemiddeld}`, :math:`r_{exit}(x,y)`, :math:`\lambda_{1}`, :math:`L_{but}`
     - :math:`Z_u`, :math:`Z_h`, :math:`Z_p`, :math:`Z_{combin}`, :math:`\phi_{exit}`, :math:`r_{exit}`, :math:`L_{kwelweg}`

   * - ``limit_state_ttim`` *(conceptueel voorbeeld)*
     - Interface voor toekomstige uitbreiding met een tijdsafhankelijk grondwatermodel (TTIM).
       Input- en outputstructuur is identiek aan de bestaande modellen.
     - :math:`\phi_{exit}`, :math:`r_{exit}`, :math:`L_{kwelweg}`, :math:`\lambda_{1}`
     - :math:`Z_u`, :math:`Z_h`, :math:`Z_p`, :math:`Z_{combin}`

Alle functies bevinden zich in het pakket ``geoprob_pipe.calculations`` en maken gebruik van de onderliggende
fysische berekeningen uit ``geoprob_pipe.calculations.physical_components.piping``.
Door deze eenduidige structuur kan elk modeltype afzonderlijk worden aangeroepen in de probabilistische analyse,
zonder dat de onderliggende rekenlogica hoeft te worden aangepast.