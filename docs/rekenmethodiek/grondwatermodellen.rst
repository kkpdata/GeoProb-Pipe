.. _stijghoogtemodellen-geoprob:
Grondwatermodellen in GeoProb-Pipe
==================================

De berekening van de stijghoogte :math:`\phi_{exit}` wordt uitgevoerd binnen de limit-state functies,
waarbij elke functie een specifiek type stijghoogtemodel aanroept:

- ``limit_state_wbi`` – eenvoudige benadering met vaste responsfactor;
- ``limit_state_model4a`` – analytisch grondwatermodel 4A (doorsnede);
- ``limit_state_moria`` – numeriek rastermodel (zoals het regionale grondwatermodel MORIA).

De rekenmethodiek is zodanig opgezet dat in de toekomst ook andere stijghoogtemodellen kunnen worden toegevoegd.

.. _model4a:

Analytische stijghoogtemodel 4A
-------------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
-----------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
---------------------------------------
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